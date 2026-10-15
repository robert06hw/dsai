"""First-round controlled representation experiment. Python 3.10+, numpy only."""
from __future__ import annotations
import argparse, ast, copy, csv, hashlib, json, math, os, platform, random
import re, subprocess, sys, time, urllib.request
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent
MODEL = 'qwen2.5-coder:3b-instruct-q4_K_M'
BASE = 'http://127.0.0.1:11435'
REPS = ['expression', 'temporary', 'meaningful']
EXPRS = {
    'P1': '-(bins - item)',
    'P2': 'bins - item',
    'P3': '-(((bins - item) - 20.0) * ((bins - item) - 20.0))',
    'P4': '(-(((bins - item) * (bins - item)) / (bins + 1.0))) + (0.2 * (bins - item))',
}
PROMPT = '''Modify this bin-scoring function to reduce the number of bins used in online bin packing. Keep the interface score(item, bins), and output only Python code.
item is a positive float; bins is a nonempty 1D numpy float64 array of feasible remaining capacities, each >= item. Capacity is 100. The evaluator preallocates one empty bin per item, scores all feasible bins, chooses the highest score, and breaks ties by the earliest bin index. Item order is fixed.
Return a finite numpy float64 array with exactly the same shape as bins. Use one pure deterministic function with straight-line local assignments and a return. numpy is already available as np. You may import numpy as np. Use numpy vector operations; do not use loops, helper functions, randomness, I/O, external state, or modify bins. No reflections or explanation.
Parent function:
{code}'''
SYSTEM = 'You are a Python programmer. Return only the modified score function.'

def sha(data):
    if isinstance(data, str): data = data.encode('utf-8')
    return hashlib.sha256(data).hexdigest()

def save(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding='utf-8')

def load(path): return json.loads(Path(path).read_text(encoding='utf-8'))

def api(path, data=None, timeout=300):
    body = None if data is None else json.dumps(data).encode()
    req = urllib.request.Request(BASE+path, data=body, headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.load(response)

def representations(expr):
    tree = ast.parse(expr, mode='eval').body
    result = {'expression': f'def score(item, bins):\n    return {expr}\n'}
    for rep in REPS[1:]:
        lines, cache = [], {}
        def walk(node):
            if isinstance(node, (ast.Name, ast.Constant)): return ast.unparse(node)
            key = ast.dump(node, include_attributes=False)
            if key in cache: return cache[key]
            if isinstance(node, ast.BinOp):
                a,b = walk(node.left),walk(node.right)
                op={ast.Add:'+',ast.Sub:'-',ast.Mult:'*',ast.Div:'/'}[type(node.op)]
                rhs=f'({a} {op} {b})'
            elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
                rhs=f'-({walk(node.operand)})'
            else: raise ValueError('Unsupported parent operation')
            number=len(lines)+1
            if rep=='temporary': name=f'v{number}'
            else:
                if isinstance(node,ast.BinOp) and ast.unparse(node)=='bins - item': name='residual'
                elif isinstance(node,ast.BinOp) and isinstance(node.op,ast.Mult): name=f'product_{number}'
                elif isinstance(node,ast.BinOp) and isinstance(node.op,ast.Div): name=f'normalized_penalty_{number}'
                elif isinstance(node,ast.UnaryOp): name=f'negative_penalty_{number}'
                elif isinstance(node,ast.BinOp) and isinstance(node.op,ast.Sub): name=f'target_distance_{number}'
                else: name=f'adjustment_{number}'
            lines.append(f'    {name} = {rhs}')
            cache[key]=name
            return name
        returned=walk(tree)
        result[rep]='def score(item, bins):\n'+'\n'.join(lines)+f'\n    return {returned}\n'
    return result

def canonical(code):
    fn=ast.parse(code).body[0]
    assert isinstance(fn,ast.FunctionDef) and [a.arg for a in fn.args.args]==['item','bins']
    env={}
    class Expand(ast.NodeTransformer):
        def visit_Name(self,node):
            return copy.deepcopy(env[node.id]) if node.id in env else node
    for statement in fn.body:
        if isinstance(statement, ast.Assign):
            assert len(statement.targets)==1 and isinstance(statement.targets[0],ast.Name)
            env[statement.targets[0].id]=Expand().visit(copy.deepcopy(statement.value))
        elif isinstance(statement,ast.Return):
            expanded=Expand().visit(copy.deepcopy(statement.value))
            return ast.dump(expanded,include_attributes=False)
        else: raise ValueError('Not a parent DSL program')
    raise ValueError('Missing return')

NP_CALLS = {'abs','absolute','sqrt','square','log','log1p','exp','expm1','maximum','minimum',
    'where','clip','power','tanh','sin','cos','floor','ceil','round','sign','zeros_like',
    'ones_like','full_like','mean','sum','min','max','std','median','percentile','quantile',
    'argmin','argmax','arange','array','asarray','stack','select','multiply','negative','logical_and','any','argsort','log2','divide','subtract','prod'}
NP_ATTRS = NP_CALLS | {'float64','pi','e','newaxis','inf','nan'}
BUILTINS = {'abs':abs,'min':min,'max':max,'float':float,'int':int,'len':len,'round':round}
ALLOWED = (ast.Module,ast.FunctionDef,ast.arguments,ast.arg,ast.Assign,ast.Return,ast.Expr,
    ast.Constant,ast.Name,ast.Load,ast.Store,ast.BinOp,ast.UnaryOp,ast.Compare,ast.Call,
    ast.Attribute,ast.keyword,ast.Subscript,ast.Slice,ast.List,ast.Tuple,ast.IfExp,
    ast.Add,ast.Sub,ast.Mult,ast.Div,ast.FloorDiv,ast.Pow,ast.Mod,ast.USub,ast.UAdd,ast.Invert,
    ast.BitAnd,ast.BitOr,ast.Eq,ast.NotEq,ast.Lt,ast.LtE,ast.Gt,ast.GtE)

def extract(raw):
    text=raw.strip()
    fenced=re.fullmatch(r'```(?:python)?\s*\n(.*?)\n```',text,re.S)
    if fenced: text=fenced.group(1)
    return text.strip()+'\n'

def compile_score(code):
    tree=ast.parse(code)
    body=[]
    for statement in tree.body:
        if isinstance(statement,ast.Import):
            if len(statement.names)!=1 or statement.names[0].name!='numpy' or statement.names[0].asname!='np':
                raise ValueError('Only import numpy as np permitted')
        else: body.append(statement)
    tree.body=body
    if len(body)!=1 or not isinstance(body[0],ast.FunctionDef) or body[0].name!='score':
        raise ValueError('Exactly one score function required')
    fn=body[0]
    if fn.decorator_list or fn.returns or fn.args.defaults or fn.args.kwonlyargs or fn.args.vararg or fn.args.kwarg or fn.args.posonlyargs:
        raise ValueError('Unsupported signature/decorators')
    if [a.arg for a in fn.args.args]!=['item','bins']: raise ValueError('Interface must be score(item, bins)')
    for a in fn.args.args: a.annotation=None
    names={'item','bins','np'} | set(BUILTINS)
    returned=False
    for s in fn.body:
        if returned: raise ValueError('Statements after return')
        if isinstance(s,ast.Expr) and isinstance(s.value,ast.Constant) and isinstance(s.value.value,str): continue
        if not isinstance(s,(ast.Assign,ast.Return)): raise ValueError('Straight-line assignments and return only')
        for node in ast.walk(s):
            if not isinstance(node,ALLOWED): raise ValueError('Unsupported node: '+type(node).__name__)
            if isinstance(node,ast.Name) and isinstance(node.ctx,ast.Load) and node.id not in names:
                raise ValueError('Unknown local name: '+node.id)
            if isinstance(node,ast.Attribute):
                numpy_attr=isinstance(node.value,ast.Name) and node.value.id=='np' and node.attr in NP_ATTRS
                derived_array=isinstance(node.value,(ast.Call,ast.Subscript,ast.BinOp,ast.UnaryOp,ast.IfExp)) or (isinstance(node.value,ast.Name) and node.value.id in names and node.value.id!='np')
                array_metadata=derived_array and node.attr in {'size','shape','ndim','dtype'}
                pure_array_method=node.attr in {'reshape','astype'} and derived_array
                pure_ufunc_method=node.attr in {'reduce','accumulate'} and isinstance(node.value,ast.Attribute) and isinstance(node.value.value,ast.Name) and node.value.value.id=='np' and node.value.attr in {'maximum','minimum'}
                if not (numpy_attr or array_metadata or pure_array_method or pure_ufunc_method):
                    raise ValueError('Unsupported attribute')
            if isinstance(node,ast.Call):
                if isinstance(node.func,ast.Name):
                    if node.func.id not in BUILTINS: raise ValueError('Unsupported call')
                elif isinstance(node.func,ast.Attribute):
                    if node.func.attr not in NP_CALLS | {'reshape','astype','reduce','accumulate'}: raise ValueError('Unsupported numpy call')
                else: raise ValueError('Unsupported call expression')
        if isinstance(s,ast.Assign):
            if len(s.targets)!=1 or not isinstance(s.targets[0],ast.Name): raise ValueError('Local name assignments only')
            name=s.targets[0].id
            if name in {'item','bins','np'} or name.startswith('_') or name in BUILTINS:
                raise ValueError('Input/state modification forbidden')
            names.add(name)
        else: returned=True
    if not returned: raise ValueError('Missing return')
    namespace={'np':np,'__builtins__':BUILTINS}
    exec(compile(ast.fix_missing_locations(tree),'<candidate>','exec'),namespace)
    return namespace['score']

def pack(items,score,capacity=100.0,score_hash=False):
    bins=np.full(len(items),capacity,dtype=np.float64)
    decisions=[]
    digest=hashlib.sha256()
    for item in items:
        indices=np.flatnonzero(bins>=item)
        feasible=bins[indices].copy()
        feasible.setflags(write=False)
        with np.errstate(all='raise'):
            values=score(float(item),feasible)
        if not isinstance(values,np.ndarray) or values.shape!=feasible.shape or values.dtype.kind not in 'fi':
            raise ValueError('Output must be numerical ndarray matching bins shape')
        values=np.asarray(values,dtype=np.float64)
        if not np.all(np.isfinite(values)): raise ValueError('Nonfinite output')
        if score_hash: digest.update(values.tobytes())
        chosen=int(indices[np.argmax(values)])
        bins[chosen]-=item
        assert bins[chosen]>=0
        decisions.append(chosen)
    return {'bins':int(np.count_nonzero(bins!=capacity)),
            'trace_hash':sha(np.asarray(decisions,dtype=np.int32).tobytes()),
            'score_hash':digest.hexdigest() if score_hash else None}

def evaluate(code,datasets):
    score=compile_score(code)
    results={}
    for split,instances in datasets.items():
        rows=[]
        for instance in instances:
            p=pack(instance['items'],score)
            p.update(id=instance['id'],lb=math.ceil(sum(instance['items'])/100))
            rows.append(p)
        results[split]={'mean_bins':float(np.mean([r['bins'] for r in rows])),
            'mean_excess_lb':float(np.mean([(r['bins']-r['lb'])/r['lb'] for r in rows])),
            'instances':rows}
    return results

def prepare():
    ROOT.joinpath('parents').mkdir(exist_ok=True)
    ROOT.joinpath('raw').mkdir(exist_ok=True)
    ROOT.joinpath('children').mkdir(exist_ok=True)
    datasets={}
    for split,seed in [('explore',2026100301),('check',2026100302)]:
        rng=np.random.default_rng(seed)
        rows=[]
        for distribution in ['uniform','weibull','bimodal','discrete']:
            for k in range(8):
                if distribution=='uniform': items=rng.integers(1,100,256)
                elif distribution=='weibull': items=np.clip(np.rint(rng.weibull(3.0,256)*45),1,99).astype(int)
                elif distribution=='bimodal': items=np.where(rng.random(256)<0.5,rng.integers(1,31,256),rng.integers(55,86,256))
                else: items=rng.choice([20,30,40,60,70,80],256)
                rows.append({'id':f'{split}_{distribution}_{k:02d}','distribution':distribution,'capacity':100,'items':items.tolist()})
        datasets[split]=rows
    save(ROOT/'datasets.json',datasets)
    parents,verification={},[]
    for pid,expr in EXPRS.items():
        programs=representations(expr)
        trees=[canonical(code) for code in programs.values()]
        assert len(set(trees))==1
        functions=[compile_score(code) for code in programs.values()]
        checked=0
        for instances in datasets.values():
            for instance in instances:
                runs=[pack(instance['items'],f,score_hash=True) for f in functions]
                assert all(r==runs[0] for r in runs)
                checked+=1
        baseline=evaluate(programs['expression'],datasets)
        parents[pid]={'expression':expr,'programs':programs,'canonical_ast':trees[0],'baseline':baseline}
        for rep,code in programs.items(): (ROOT/'parents'/f'{pid}_{rep}.py').write_text(code,encoding='utf-8')
        verification.append({'parent':pid,'ast_equal':True,'score_decision_bin_equal':True,'instances_checked':checked,
            'explore_mean_bins':baseline['explore']['mean_bins'],'check_mean_bins':baseline['check']['mean_bins']})
    save(ROOT/'parents.json',parents)
    save(ROOT/'equivalence.json',verification)
    schedule=[]
    for i,pid in enumerate(EXPRS):
        for rep in REPS:
            for k in range(8):
                schedule.append({'id':f'{pid}_{rep}_{k:02d}','parent':pid,'representation':rep,'sample':k,'seed':20261003+i*100+k})
    random.Random(20261003).shuffle(schedule)
    config={'model':MODEL,'temperature':0.7,'top_p':0.9,'top_k':40,'num_predict':512,'num_ctx':2048,
        'generation_timeout_seconds':300,'evaluation_timeout_seconds':30,'system':SYSTEM,'prompt_template':PROMPT,
        'capacity':100,'items_per_instance':256,'instances_per_split':32,'split_seeds':[2026100301,2026100302],
        'schedule':schedule,'paired_seeds_across_representations':True,'no_feedback':True,
        'evaluator':'EoH-compatible feasibility/argmax/first-index ties, synthetic fixed 64 instances; not full EoH evolution',
        'primary_metric':'strictly lower mean used bins than same parent, separately on each split',
        'dataset_sha256':sha((ROOT/'datasets.json').read_bytes()),'parent_sha256':sha((ROOT/'parents.json').read_bytes()),
        'script_sha256':sha(Path(__file__).read_bytes()),'python':sys.version,'numpy':np.__version__,'platform':platform.platform()}
    save(ROOT/'config.json',config)
    print(json.dumps(verification,indent=2),flush=True)

def worker(code_path,result_path):
    started=time.perf_counter()
    try:
        result={'valid':True,'metrics':evaluate(Path(code_path).read_text(encoding='utf-8'),load(ROOT/'datasets.json'))}
    except Exception as error:
        result={'valid':False,'error_type':type(error).__name__,'error':str(error)}
    result['evaluation_seconds']=time.perf_counter()-started
    save(result_path,result)

def run():
    config=load(ROOT/'config.json')
    assert sha((ROOT/'datasets.json').read_bytes())==config['dataset_sha256']
    assert sha((ROOT/'parents.json').read_bytes())==config['parent_sha256']
    parents=load(ROOT/'parents.json')
    if not (ROOT/'model_metadata.json').exists():
        save(ROOT/'model_metadata.json',{'tags':api('/api/tags'),'show':api('/api/show',{'model':MODEL}),'version':api('/api/version')})
    log=ROOT/'records.jsonl'
    done={load(p)['id'] for p in (ROOT/'raw').glob('*.json') if load(p).get('finalized')}
    for number,entry in enumerate(config['schedule'],1):
        if entry['id'] in done: continue
        path=ROOT/'raw'/(entry['id']+'.json')
        code=parents[entry['parent']]['programs'][entry['representation']]
        request={'model':MODEL,'system':SYSTEM,'prompt':PROMPT.format(code=code),'stream':False,'keep_alive':'30m',
            'options':{k:config[k] for k in ['temperature','top_p','top_k','num_predict','num_ctx']}}
        request['options']['seed']=entry['seed']
        # Never issue another generation for an already recorded response.
        if path.exists(): record=load(path)
        else:
            record={**entry,'request':request,'started_unix':time.time()}
            start=time.perf_counter()
            try: record['response']=api('/api/generate',request,config['generation_timeout_seconds'])
            except Exception as error: record['generation_error']=str(error)
            record['generation_seconds']=time.perf_counter()-start
            save(path,record)
        if 'response' in record:
            candidate=extract(record['response'].get('response',''))
            child=ROOT/'children'/(entry['id']+'.py')
            child.write_text(candidate,encoding='utf-8')
            result=ROOT/'children'/(entry['id']+'.evaluation.json')
            try:
                process=subprocess.run([sys.executable,str(ROOT/'experiment.py'),'worker',str(child),str(result)],
                    timeout=config['evaluation_timeout_seconds'],capture_output=True,text=True,encoding='utf-8')
                if process.returncode or not result.exists():
                    record['evaluation']={'valid':False,'error_type':'WorkerFailure','error':process.stderr[-1000:]}
                else: record['evaluation']=load(result)
            except subprocess.TimeoutExpired:
                record['evaluation']={'valid':False,'error_type':'Timeout','error':'30-second evaluation timeout'}
            record['candidate_sha256']=sha(candidate)
        else: record['evaluation']={'valid':False,'error_type':'GenerationFailure','error':record['generation_error']}
        if record['evaluation']['valid']:
            for split,m in record['evaluation']['metrics'].items():
                baseline=parents[entry['parent']]['baseline'][split]
                m['delta_bins']=baseline['mean_bins']-m['mean_bins']
                m['improved']=m['delta_bins']>0
                m['different_decision_instances']=sum(a['trace_hash']!=b['trace_hash'] for a,b in zip(m['instances'],baseline['instances']))
        record['finalized']=True
        save(path,record)
        with log.open('a',encoding='utf-8') as f: f.write(json.dumps(record,ensure_ascii=False)+'\n')
        valid=record['evaluation']['valid']
        metric=record['evaluation'].get('metrics',{}).get('check',{})
        print(f"{number}/96 {entry['id']} valid={valid} check_delta={metric.get('delta_bins')} tokens={record.get('response',{}).get('eval_count')} seconds={record['generation_seconds']:.1f}",flush=True)
    summarize()

def summarize():
    records=[load(p) for p in (ROOT/'raw').glob('*.json') if load(p).get('finalized')]
    rows=[]
    for pid in EXPRS:
        for rep in REPS:
            group=[r for r in records if r['parent']==pid and r['representation']==rep]
            valid=[r for r in group if r['evaluation']['valid']]
            row={'parent':pid,'representation':rep,'generated':len(group),'executable':len(valid)}
            for split in ['explore','check']:
                row[split+'_improved']=sum(r['evaluation']['metrics'][split]['improved'] for r in valid)
                row[split+'_mean_delta_valid']=float(np.mean([r['evaluation']['metrics'][split]['delta_bins'] for r in valid])) if valid else None
                row[split+'_best_delta']=max([r['evaluation']['metrics'][split]['delta_bins'] for r in valid],default=None)
                row[split+'_mean_behavior_different_instances']=float(np.mean([r['evaluation']['metrics'][split]['different_decision_instances'] for r in valid])) if valid else None
            for field,key in [('mean_input_tokens','prompt_eval_count'),('mean_output_tokens','eval_count')]:
                values=[r['response'][key] for r in group if key in r.get('response',{})]
                row[field]=float(np.mean(values)) if values else None
            row['mean_total_tokens']=row['mean_input_tokens']+row['mean_output_tokens'] if row['mean_input_tokens'] is not None else None
            row['mean_generation_seconds']=float(np.mean([r['generation_seconds'] for r in group])) if group else None
            rows.append(row)
    if rows:
        with (ROOT/'summary.csv').open('w',newline='',encoding='utf-8-sig') as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    errors={}
    for r in records:
        if not r['evaluation']['valid']:
            key=r['evaluation']['error_type']+': '+r['evaluation']['error']
            errors[key]=errors.get(key,0)+1
    save(ROOT/'summary.json',{'completed':len(records),'valid':sum(r['evaluation']['valid'] for r in records),
        'generation_seconds':sum(r['generation_seconds'] for r in records),
        'input_tokens':sum(r.get('response',{}).get('prompt_eval_count',0) for r in records),
        'output_tokens':sum(r.get('response',{}).get('eval_count',0) for r in records),
        'errors':errors,'rows':rows})
    print(json.dumps({'completed':len(records),'errors':errors}),flush=True)

if __name__=='__main__':
    cmd=sys.argv[1] if len(sys.argv)>1 else 'prepare'
    if cmd=='prepare': prepare()
    elif cmd=='run': run()
    elif cmd=='worker': worker(sys.argv[2],sys.argv[3])
    elif cmd=='summarize': summarize()
    else: raise SystemExit('prepare | run | worker CODE OUTPUT | summarize')
