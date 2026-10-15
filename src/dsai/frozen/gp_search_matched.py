"""Limited initialization CPU GP, frozen proper fragments, zero model calls."""
import ast, collections, concurrent.futures, copy, json, os, subprocess, sys, time, warnings
from pathlib import Path
import cpu as c
import typed_tree as t
import historical_validator as v
import historical_prior as prior
import numpy as np
ROOT=Path(__file__).resolve().parent
OLD=ROOT.parent/'fragment_gp_01'
METHODS=['matched_random_fragment_gp']
SEEDS=[303, 404, 505, 606, 707, 808, 909, 1010, 1111, 1212, 1313, 1414, 1515, 1616, 1717, 1818, 1919, 2020, 2121, 2222, 2323, 2424, 2525, 2626, 2727, 2828, 2929, 3030, 3131, 3232]

def save(path,obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix(path.suffix+f'.{os.getpid()}.tmp')
    tmp.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    for i in range(30):
        try:tmp.replace(path);return
        except PermissionError:
            if i==29:raise
            time.sleep(.05)

def enc(node):
    if isinstance(node,ast.AST):return {'_ast':type(node).__name__,**{f:enc(getattr(node,f)) for f in node._fields}}
    if isinstance(node,list):return [enc(x) for x in node]
    return node

def dec(obj):
    if isinstance(obj,dict) and '_ast' in obj:return getattr(ast,obj['_ast'])(**{k:dec(x) for k,x in obj.items() if k!='_ast'})
    if isinstance(obj,list):return [dec(x) for x in obj]
    return obj

def rng(seed,attempt,channel):return np.random.default_rng(np.random.SeedSequence([seed,attempt,channel]))
def choice(items,r):return items[int(r.integers(len(items)))]

def payload(node):
    expression=t.text(node);emitted=t.parse(expression)
    return {'tree':enc(node),'expression':expression,'internal_key':t.key(node),'execution_key':t.key(emitted),
            'internal_nodes':t.size(node),'internal_depth':t.depth(node),'nodes':t.size(emitted),'depth':t.depth(emitted),'type':t.infer(node)}

def limits(p):
    if p['type']!='V':return 'Root must be numeric bin-score vector'
    if p['nodes']>64 or p['depth']>8:return f"SizeLimit: nodes={p['nodes']},depth={p['depth']}"
    return ''

def order(record):return (record['mean_bins'],record['nodes'],record['execution_key'])
def selection(population):
    unique={}
    for row in sorted(population,key=order):unique.setdefault(row['execution_key'],row)
    return sorted(unique.values(),key=order)[:16]

def operator_test():
    # Boundary counting uses emitted source, so negative constants cannot evade size limits.
    assert payload(ast.Constant(value=-5.0))['nodes']==2
    mask=t.parse('bins > item');root=t.parse('np.where(bins > item, -bins, 0.0)')
    loc=next(path for path,node,kind in t.locations(root) if kind=='BV')
    assert t.infer(t.replace(root,loc,mask))=='V'
    huge=t.parse('bins')
    for _ in range(9):huge=t.call('square',huge)
    assert limits(payload(huge)).startswith('SizeLimit')
    x={'mean_bins':2000.,'nodes':5,'execution_key':'a','id':'x'}
    y={'mean_bins':2001.,'nodes':1,'execution_key':'b','id':'y'}
    assert selection([x,y,x])==[x,y]
    return {'emitted_negative_literal_counted':True,'typed_mask_crossover':True,'depth_limit_checked':True,'elitism_and_structural_duplicates':True}

def prepare():
    raise RuntimeError('Use setup_matched.py for frozen shared initialization')

def check_lock():
    for rel,h in c.load(ROOT/'pre_search_lock.json')['files'].items():assert c.sha((ROOT/rel).read_bytes())==h,rel

def worker(jobpath,outpath):
    job=c.load(jobpath);p=job['candidate'];start=time.perf_counter();resource=c.memory_limit()
    result={'id':p['id'],'split':job['split'],'valid':False,'error':'','instances':[],'resource_limit':resource}
    try:
        assert p.get('reference_name') or not limits(p)
        fn=c.trusted(p['reference_name']) if p.get('reference_name') else v.compile_score(t.program(dec(p['tree'])))
        traces={}
        with warnings.catch_warnings(record=True) as ws:
            warnings.simplefilter('once')
            for inst in c.data(job['split']):
                row,idx,caps=c.pack(inst,fn);result['instances'].append({'instance_id':inst['id'],**row})
                traces['indices_'+inst['id']]=idx;traces['capacities_'+inst['id']]=caps
            result['warnings']=sorted(set(str(w.message) for w in ws))
        trace=f"traces/{job['split']}_{p['id']}.npz";np.savez_compressed(ROOT/trace,**traces)
        result.update(valid=True,mean_bins=float(np.mean([r['bins_used'] for r in result['instances']])),trace_path=trace)
    except Exception as exc:result['error']=f'{type(exc).__name__}: {exc}'
    result['worker_wall_seconds']=time.perf_counter()-start;save(outpath,result)

def evaluate(p,split='pilot_dev'):
    out=ROOT/'evaluations'/f"{split}_{p['id']}.json"
    if out.exists():return c.load(out)
    error='' if p.get('reference_name') else limits(p) or p.get('construction_error','')
    start=time.perf_counter()
    if error:
        result={'id':p['id'],'split':split,'valid':False,'error':error,'instances':[],'pre_evaluation_rejected':True}
    else:
        job=ROOT/'jobs'/f"{split}_{p['id']}.json";save(job,{'candidate':p,'split':split})
        try:
            proc=subprocess.run([sys.executable,str(ROOT/'gp_search.py'),'worker',str(job),str(out)],capture_output=True,text=True,encoding='utf-8',timeout=120)
            result=c.load(out) if proc.returncode==0 and out.exists() else {'id':p['id'],'split':split,'valid':False,'error':'WorkerFailure: '+proc.stderr[-1000:],'instances':[]}
        except subprocess.TimeoutExpired:result={'id':p['id'],'split':split,'valid':False,'error':'WorkerTimeout120s','instances':[]}
    result['evaluation_wall_seconds']=time.perf_counter()-start;save(out,result);return result

def load_library(method):
    assert method=='matched_random_fragment_gp'
    out=collections.defaultdict(list)
    rows=c.load(ROOT/'libraries/matched_random_fragments.json')
    for row in sorted(rows,key=lambda r:r['template_key']):
        node=t.parse(row['expression']);assert t.key(node)==row['key']
        out[row['type']].append((node,row['key']))
    return out

def offspring(seed,attempt,method,pop,library):
    schedule=c.load(ROOT/'operator_schedule.json')[str(seed)];op=schedule[attempt-1]
    parent=choice(pop,rng(seed,attempt,1));other=choice(pop,rng(seed,attempt,2))
    root=dec(parent['tree']);places=list(t.locations(root));path,node,kind=choice(places,rng(seed,attempt,3))
    meta={'operator':op,'parent_id':parent['id'],'second_parent_id':other['id'] if op=='crossover' else None,
        'target_path':list(path),'target_type':kind,'replacement_source':None,'fragment_key':None,'construction_error':''}
    try:
        if op=='crossover':
            choices=[(p,n) for p,n,k in t.locations(dec(other['tree'])) if k==kind]
            donor_path,donor=choice(choices,rng(seed,attempt,4));meta['donor_path']=list(donor_path)
            child=t.replace(root,path,donor)
        elif op=='subtree_replace':
            use_library=rng(seed,attempt,5).random()<.5 and method!='basic_gp'
            if use_library:
                donor,key=choice(library[kind],rng(seed,attempt,6));meta.update(replacement_source='matched_random_fragment',fragment_key=key)
                assert t.key(t.canonical(donor)) not in prior.index()['normalized'],'Full historical root insertion forbidden'
            else:
                r=rng(seed,attempt,6);donor=t.random_tree(kind,r,levels=int(r.integers(1,4)),safe=True);meta['replacement_source']='basic_operators'
            child=t.replace(root,path,donor)
        else:
            constants=[(p,n) for p,n,k in places if isinstance(n,ast.Constant) and isinstance(n.value,(float,int)) and not isinstance(n.value,bool)]
            cp,old=choice(constants,rng(seed,attempt,7));value=float(old.value)+float(rng(seed,attempt,8).normal(0,5))
            meta.update(target_path=list(cp),constant_before=old.value,constant_after=value)
            child=t.replace(root,cp,ast.Constant(value=value))
        assert t.infer(child)=='V'
    except Exception as exc:
        meta['construction_error']=f'ConstructionFailure: {type(exc).__name__}: {exc}';child=root
    p={'id':f'{method}_{seed}_{attempt:03d}','seed':seed,'method':method,'attempt':attempt,**payload(child),**meta,**prior.matches(child)}
    return p

def run_one(seed,method):
    folder=ROOT/'runs'/f'{method}_{seed}';folder.mkdir(exist_ok=True);checkpoint=folder/'checkpoint.json'
    if (folder/'complete.json').exists():return c.load(folder/'complete.json')
    initial=c.load(ROOT/'initialization/results.json')[str(seed)];initial_pop=selection([r for r in initial if r['valid']]);assert initial_pop
    if checkpoint.exists():state=c.load(checkpoint)
    else:state={'completed':0,'population':initial_pop,'best':initial_pop[0],'initial_best':initial_pop[0],
        'seen_keys':[r['execution_key'] for r in initial],'log':[],'cumulative_evaluation_seconds':sum(r['evaluation_wall_seconds'] for r in initial),
        'initial_population_ids':[r['id'] for r in initial_pop]}
    library=load_library(method)
    for attempt in range(state['completed']+1,113):
        plan=ROOT/'candidates'/f'{method}_{seed}_{attempt:03d}.json'
        if plan.exists():p=c.load(plan)
        else:p=offspring(seed,attempt,method,state['population'],library);save(plan,p)
        before=state['best'];parent=next(x for x in state['population'] if x['id']==p['parent_id'])
        previous_ids=[x['id'] for x in state['population']];duplicate=p['execution_key'] in state['seen_keys']
        result=evaluate(p);child={**p,**result,**prior.annotate_result(dec(p['tree']),result)}
        valid=result['valid'];delta=lambda q:q['mean_bins']-child['mean_bins'] if valid else None
        if valid:
            if order(child)<order(state['best']):state['best']=child
            if method!='fixed_parent_random':state['population']=selection(state['population']+[child])
        state['seen_keys'].append(p['execution_key']);state['cumulative_evaluation_seconds']+=result['evaluation_wall_seconds']
        state['log'].append({'attempt':attempt,'nominal_slot':16+attempt,'candidate_id':p['id'],'operator':p['operator'],
            'parent_id':p['parent_id'],'second_parent_id':p['second_parent_id'],'replacement_source':p['replacement_source'],'fragment_key':p['fragment_key'],
            'nodes':p['nodes'],'depth':p['depth'],'valid':valid,'duplicate':duplicate,'error':result['error'],'mean_bins':result.get('mean_bins'),
            'delta_parent':delta(parent),'delta_initial_best':delta(state['initial_best']),'delta_previous_best':delta(before),
            'improves_parent':valid and delta(parent)>0,'improves_initial_best':valid and delta(state['initial_best'])>0,
            'improves_previous_best':valid and delta(before)>0,'best_mean_bins':state['best']['mean_bins'],'best_id':state['best']['id'],
            'population_before':previous_ids,'population_after':[x['id'] for x in state['population']],
            'historical_tree_class':child['historical_tree_class'],'historical_tree_rediscovered':child['historical_tree_rediscovered'],
            'observed_historical_behavior_signature':child['observed_historical_behavior_signature'],
            'observed_historical_behavior_program_count':child['observed_historical_behavior_program_count'],
            'evaluation_wall_seconds':result['evaluation_wall_seconds'],'cumulative_evaluation_seconds':state['cumulative_evaluation_seconds']})
        state['completed']=attempt;save(checkpoint,state)
        if attempt%28==0:print(method,seed,attempt,'/112 best',state['best']['mean_bins'],flush=True)
    complete={'seed':seed,'method':method,'nominal_attempts':128,'new_child_attempts':112,'initial_best':state['initial_best'],
        'best':state['best'],'population':state['population'],'completed_at':c.now(),'LLM_requests':0}
    save(folder/'complete.json',complete);return complete

def run():
    check_lock();start=time.perf_counter();plans=c.load(ROOT/'initialization/plans.json')
    if not (ROOT/'initialization/results.json').exists():
        rows=[p for r in plans.values() for p in r]
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(evaluate,rows))
        combined={seed:[{**p,**result} for p,result in zip(rows,results) if str(p['id'].split('_')[1])==seed] for seed in plans}
        save(ROOT/'initialization/results.json',combined)
        for seed,initial in combined.items():print('Shared init',seed,'attempts',len(initial),'valid',sum(r['valid'] for r in initial),'best',min(r['mean_bins'] for r in initial if r['valid']),flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures=[pool.submit(run_one,seed,method) for seed in SEEDS for method in METHODS]
        runs=[f.result() for f in futures]
    if not (ROOT/'search_complete.json').exists():save(ROOT/'search_complete.json',{'completed_at':c.now(),'runs':30,'nominal_attempts':3840,'new_child_attempts':3360,'LLM_requests':0})
    # Only now create validation jobs; the search never uses pilot_val.
    diagnostic=[]
    for row in runs:
        p=copy.deepcopy(row['best']);p['selected_candidate_id']=p['id'];p['id']=f"final_{row['method']}_{row['seed']}";diagnostic.append(p)
    initial=c.load(ROOT/'initialization/results.json')
    for seed in SEEDS:
        p=copy.deepcopy(selection([r for r in initial[str(seed)] if r['valid']])[0]);p['id']=f'initial_best_{seed}';diagnostic.append(p)
    for name in ['Best-fit','EoH','Historical-best']:
        node,_=t.expand_program((ROOT/'rules'/f'{name}.py').read_text(encoding='utf-8'));p={'id':f'reference_{name}','reference_name':name,**payload(node)};diagnostic.append(p)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:values=list(pool.map(lambda p:evaluate(p,'pilot_val'),diagnostic))
    save(ROOT/'diagnostic_validation.json',[{'candidate':p,'evaluation':val} for p,val in zip(diagnostic,values)])
    refs=[p for p in diagnostic if p.get('reference_name')]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:ref_values=list(pool.map(evaluate,refs))
    save(ROOT/'diagnostic_reference_dev.json',[{'candidate':p,'evaluation':val} for p,val in zip(refs,ref_values)])
    save(ROOT/'execution_complete.json',{'completed_at':c.now(),'this_invocation_wall_seconds':time.perf_counter()-start,'LLM_requests':0,'nominal_attempts':3840})
    print('All 30 seed-extension searches and diagnostics complete',flush=True)

if __name__=='__main__':
    mode=sys.argv[1]
    if mode=='prepare':prepare()
    elif mode=='run':run()
    elif mode=='worker':worker(sys.argv[2],sys.argv[3])
    else:raise ValueError(mode)
