"""Bounded extraction/equivalence/calibration. CPU only; no model client."""
import ast, collections, concurrent.futures, copy, csv, json, os, shutil, subprocess, sys, time, warnings
from pathlib import Path
import cpu as c
import historical_validator as validator
import historical_purity as purity
import typed_tree as t
import numpy as np
ROOT=Path(__file__).resolve().parent
ARCHIVES=c.HISTORY+['ci_evo_ec_audit_20261004','baseline_calibration_01','behavior_stage1_01','behavior_stage2_01','behavior_stage2_v2_01']

def save(p,obj):
    """Retry only an identical serialized filesystem write, never an experiment."""
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);temp=p.with_suffix(p.suffix+f'.{os.getpid()}.tmp')
    temp.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
    for attempt in range(30):
        try:temp.replace(p);return
        except PermissionError:
            if attempt==29:raise
            time.sleep(.05)

def load(p):return c.load(p)
def check_lock(name):
    for path,digest in load(ROOT/name)['files'].items():assert c.sha((ROOT/path).read_bytes())==digest,path

def collect():
    assert not (ROOT/'source_calibration_lock.json').exists()
    checks=t.tests();c.unit_checks();save(ROOT/'tree_tests.json',checks)
    programs={}
    def add(code,origin):
        try:k=t.key(ast.parse(code))
        except Exception:k=c.sha(code)
        if k not in programs:
            path=ROOT/'source_programs'/f'{k}.py';path.write_text(code,encoding='utf-8')
            programs[k]={'program_id':k,'code_path':path.relative_to(ROOT).as_posix(),'code_sha256':c.sha(path.read_bytes()),'origins':[]}
        programs[k]['origins'].extend(origin)
    old=ROOT.parent/'behavior_stage1_01'
    quality=list(csv.DictReader((old/'candidate_quality.csv').open(encoding='utf-8-sig')))
    ids={r['candidate_id'] for r in quality};assert len(ids)==len(quality)==1242
    source_selection=[]
    registry={r['candidate_id']:r for r in load(ROOT/'sources/stage1_registry.json')}
    for source_index,candidate_id in enumerate(sorted(ids),1):
        row=registry[candidate_id];validity=load(old/'candidate_results'/f'{candidate_id}.json')
        assert validity['valid_dev'] and validity['valid_pools']
        source_path=old/row['path'];code=source_path.read_text(encoding='utf-8')
        assert c.sha(code)==row['code_sha256']
        add(code,row['origins'])
        source_selection.append({'candidate_id':candidate_id,'source_path':str(source_path),
            'source_file_sha256':c.sha(source_path.read_bytes()),'registry_code_sha256':row['code_sha256'],
            'valid_dev':True,'valid_pools':True})
        if source_index%200==0:print('Step1 verified/copied sources',source_index,'/1242',flush=True)
    assert len(programs)==1242
    save(ROOT/'sources/selected_1242.json',source_selection)
    save(ROOT/'sources/unconverted_registry.json',list(programs.values()))
    files=['pipeline.py','typed_tree.py','cpu.py','historical_validator.py','historical_purity.py','scoring.py',
        'tree_tests.json','unit_checks.json','PROTOCOL.md','README.md','sources/selected_1242.json','sources/unconverted_registry.json',
        'data/pilot_dev.jsonl','data/pilot_val.jsonl']
    files+=[p.relative_to(ROOT).as_posix() for folder in ['source_programs','rules'] for p in (ROOT/folder).glob('*.py')]
    assert c.sha((ROOT/'data/pilot_dev.jsonl').read_bytes())==c.sha((ROOT.parent/'behavior_stage2_v2_01/data/pilot_dev.jsonl').read_bytes())
    data=c.data('pilot_dev');assert len(data)==5
    assert all(r['capacity']==100 and r['num_items']==5000 and len(r['items'])==5000 for r in data)
    save(ROOT/'source_calibration_lock.json',{'locked_at':c.now(),'source_programs':1242,'GP_attempts':0,'LLM_requests':0,
        'files':{name:c.sha((ROOT/name).read_bytes()) for name in files}})
    print('Step1 sources locked: exactly1242 valid historical programs, unchanged five pilot_dev instances',flush=True)

def prepare():
    assert not (ROOT/'extraction_lock.json').exists()
    check_lock('source_calibration_lock.json');assert load(ROOT/'extraction/calibration_gate.json')['passed']
    programs={r['program_id']:r for r in load(ROOT/'sources/unconverted_registry.json')}
    rows=[]
    for i,(key,row) in enumerate(programs.items(),1):
        code=(ROOT/row['code_path']).read_text(encoding='utf-8')
        try:
            validator.compile_score(code);purity.check_purity(ast.parse(code))
            expression,dependencies=t.expand_program(code)
            row.update(convertible=True,expression=t.text(expression),expression_key=t.key(expression),
                normalized_expression=t.text(t.canonical(expression)),normalized_key=t.key(t.canonical(expression)),
                size=t.size(expression),depth=t.depth(expression),dependencies=dependencies,error='')
        except Exception as exc:row.update(convertible=False,error=f'{type(exc).__name__}: {exc}')
        rows.append(row)
        if i%200==0:print('static extraction',i,'/',len(programs),flush=True)
    save(ROOT/'sources/program_registry.json',rows)
    rng=np.random.default_rng(7301);probes=[]
    for i in range(64):
        item=float(rng.integers(1,100));length=[1,2,4,8,16,32,64,128][i%8]
        caps=rng.integers(int(item),101,length).astype(float)
        if i%4==0:caps[:]=max(item,50)
        probes.append({'id':i,'item':item,'caps':caps.tolist()})
    save(ROOT/'extraction/score_probes.json',probes)
    archives={name:c.sha((ROOT.parent/name/'manifest.json').read_bytes()) for name in ARCHIVES}
    save(ROOT/'source_archive_lock.json',archives)
    config={'experiment':'fragment_gp_01','LLM_requests':0,'source_quality_filter':False,
        'source_programs':len(rows),'convertible_static':sum(r['convertible'] for r in rows),
        'extraction_score_probes':64,'score_comparison':'exact shape/dtype/value with equal_nan; all packing states also checked',
        'data':'unchanged pilot_dev6001..6005; pilot_val copied but NOT evaluated in these three steps',
        'expansion_safety_nodes':4096,'expansion_safety_depth':64,
        'worker_count':4,'worker_timeout_seconds':120,'memory_bytes_per_worker':536870912,'blas_threads':1,
        'no_behavior_pruning':True,'fragment_library_source':'supported AND full-pilot_dev valid AND exact-equivalence checked programs; no quality selection',
        'normalization':'unary plus removal, literal unary sign folding, double negation only; no associative/commutative reorder',
        'raw_structural_duplicates':'one structural payload, all occurrence/source multiplicity retained; no behavior pruning',
        'clean_library':'one normalized structural payload per type; sampling/search NOT executed',
        'scope':'Only data calibration, exact program conversion verification, and frozen two libraries',
        'source_selection':'all and only existing1242 valid_dev AND valid_pools programs; no stage2 additions',
        'GP_attempts':0}
    save(ROOT/'extraction_config.json',config)
    files=['pipeline.py','typed_tree.py','cpu.py','historical_validator.py','historical_purity.py','scoring.py',
        'tree_tests.json','unit_checks.json','extraction_config.json','source_archive_lock.json','sources/program_registry.json','sources/selected_1242.json','extraction/score_probes.json',
        'data/pilot_dev.jsonl','data/pilot_val.jsonl','PROTOCOL.md','README.md']
    files += [p.relative_to(ROOT).as_posix() for p in (ROOT/'source_programs').glob('*.py')]
    files += [p.relative_to(ROOT).as_posix() for p in (ROOT/'rules').glob('*.py')]
    save(ROOT/'extraction_lock.json',{'locked_at':c.now(),'files':{name:c.sha((ROOT/name).read_bytes()) for name in files}})
    print('Extraction locked:',len(rows),'sources;',config['convertible_static'],'static convertible',flush=True)

def calibration():
    check_lock('source_calibration_lock.json');results=[];prior=list(csv.DictReader((ROOT.parent/'behavior_stage2_v2_01/reference_pilot_dev.csv').open(encoding='utf-8-sig')))
    historical=load(ROOT.parent/'behavior_stage2_v2_01/reference_results/Historical-best_pilot_dev.json')
    for name in ['Best-fit','EoH','Historical-best']:
        path=ROOT/'extraction/calibration'/f'{name}.json';job=ROOT/'jobs'/f'calibration_{name}.json'
        if not path.exists():
            save(job,{'reference':name});start=time.perf_counter()
            proc=subprocess.run([sys.executable,str(ROOT/'pipeline.py'),'reference',str(job),str(path)],capture_output=True,text=True,encoding='utf-8',timeout=120)
            assert proc.returncode==0 and path.exists(),proc.stderr
            result=load(path);result['subprocess_wall_seconds']=time.perf_counter()-start;save(path,result)
        result=load(path);assert result['valid'],result.get('error')
        for r in result['instances']:
            expected=next(x for x in historical['instances'] if x['instance_id']==r['instance_id']) if name=='Historical-best' else next(x for x in prior if x['heuristic']==name and x['instance_id']==r['instance_id'])
            assert r['bins_used']==int(expected['bins_used']) and r['trace_hash']==expected['trace_hash'] and r['chosen_capacity_hash']==expected['chosen_capacity_hash']
        assert result['mean_bins']=={'Best-fit':2066.4,'EoH':2059.4,'Historical-best':2044.8}[name]
        results.append({'heuristic':name,'mean_bins':result['mean_bins'],'instances':len(result['instances']),
            'prior_bins_and_complete_decisions_reproduced':True,'subprocess_wall_seconds':result['subprocess_wall_seconds']})
    c.table(ROOT/'extraction/calibration_summary.csv',results)
    save(ROOT/'extraction/calibration_gate.json',{'passed':True,'LLM_requests':0,'results':results,'checked_at':c.now()})
    print('Calibration reproduced:',json.dumps(results,ensure_ascii=False),flush=True)

def reference_worker(jobpath,outpath):
    name=load(jobpath)['reference'];resource=c.memory_limit();start=time.perf_counter();result={'valid':False,'instances':[],'error':'','resource_limit':resource}
    try:
        fn=c.trusted(name);traces={}
        with warnings.catch_warnings(record=True) as ws:
            warnings.simplefilter('once')
            for inst in c.data('pilot_dev'):
                row,indices,caps=c.pack(inst,fn);result['instances'].append({'instance_id':inst['id'],**row})
                traces['indices_'+inst['id']]=indices;traces['capacities_'+inst['id']]=caps
            result['warnings']=sorted(set(str(w.message) for w in ws))
        np.savez_compressed(ROOT/'traces'/f'calibration_{name}.npz',**traces)
        result.update(valid=True,mean_bins=float(np.mean([r['bins_used'] for r in result['instances']])))
    except Exception as exc:result['error']=f'{type(exc).__name__}: {exc}'
    result['wall_seconds']=time.perf_counter()-start;save(outpath,result)

def compare_values(a,b):
    aa=np.asarray(a);bb=np.asarray(b)
    return aa.shape==bb.shape and aa.dtype==bb.dtype and np.array_equal(aa,bb,equal_nan=True)

def extraction_worker(jobpath,outpath):
    job=load(jobpath);row=job['program'];start=time.perf_counter();resource=c.memory_limit()
    result={'program_id':row['program_id'],'valid':False,'error':'','instances':[],
        'probe_score_comparisons':0,'packing_state_score_comparisons':0,'nonfinite_probe_outputs':0,'resource_limit':resource,'started_at':c.now()}
    try:
        orig=validator.compile_score((ROOT/row['code_path']).read_text(encoding='utf-8'))
        expression=t.parse(row['expression']);normalized=t.canonical(expression)
        raw=validator.compile_score(t.program(expression));clean=validator.compile_score(t.program(normalized))
        with warnings.catch_warnings(record=True) as ws:
            warnings.simplefilter('once')
            for probe in load(ROOT/'extraction/score_probes.json'):
                caps=np.asarray(probe['caps'],dtype=np.float64);caps.setflags(write=False)
                values=[];exceptions=[]
                for fn in [orig,raw,clean]:
                    try:values.append(fn(probe['item'],caps));exceptions.append(None)
                    except Exception as exc:values.append(None);exceptions.append((type(exc).__name__,str(exc)))
                if any(exceptions):
                    if not (exceptions[0]==exceptions[1]==exceptions[2]):raise ValueError('ScoreMismatch on probe exception behavior')
                    result['matched_probe_exceptions']=result.get('matched_probe_exceptions',0)+1
                    result['probe_score_comparisons']+=1
                    continue
                a,b,d=values
                if not compare_values(a,b) or not compare_values(a,d):raise ValueError('ScoreMismatch on fixed legal probe')
                result['probe_score_comparisons']+=1
                if not np.all(np.isfinite(np.asarray(a))):result['nonfinite_probe_outputs']+=1
            def checked(item,bins):
                a=orig(item,bins);b=raw(item,bins);d=clean(item,bins)
                if not compare_values(a,b) or not compare_values(a,d):raise ValueError('ScoreMismatch on original complete packing trajectory')
                result['packing_state_score_comparisons']+=1
                return a
            traces={}
            for inst in c.data('pilot_dev'):
                before,idx0,cap0=c.pack(inst,checked)
                after,idx1,cap1=c.pack(inst,raw)
                normalized_result,idx2,cap2=c.pack(inst,clean)
                for converted,indices,caps in [(after,idx1,cap1),(normalized_result,idx2,cap2)]:
                    if before['bins_used']!=converted['bins_used'] or not np.array_equal(idx0,indices) or not np.array_equal(cap0,caps):
                        raise ValueError('PackingMismatch')
                result['instances'].append({'instance_id':inst['id'],'original_bins':before['bins_used'],
                    'expanded_bins':after['bins_used'],'normalized_bins':normalized_result['bins_used'],
                    'trace_hash':before['trace_hash'],'capacity_hash':before['chosen_capacity_hash'],
                    'original_checked_runtime':before['runtime'],'expanded_runtime':after['runtime'],'normalized_runtime':normalized_result['runtime']})
                traces['indices_'+inst['id']]=idx1;traces['capacities_'+inst['id']]=cap1
            result['warnings']=sorted(set(str(w.message) for w in ws))
        trace_path=ROOT/'traces'/f"extract_{row['program_id']}.npz";np.savez_compressed(trace_path,**traces)
        result.update(valid=True,mean_bins=float(np.mean([r['original_bins'] for r in result['instances']])),trace_path=trace_path.relative_to(ROOT).as_posix())
    except Exception as exc:result['error']=f'{type(exc).__name__}: {exc}'
    result.update(wall_seconds=time.perf_counter()-start,completed_at=c.now());save(outpath,result)

def dispatch(row):
    path=ROOT/'extraction/results'/f"{row['program_id']}.json"
    if path.exists():return load(path)
    job=ROOT/'jobs'/f"extract_{row['program_id']}.json";save(job,{'program':row})
    start=time.perf_counter()
    try:
        proc=subprocess.run([sys.executable,str(ROOT/'pipeline.py'),'worker',str(job),str(path)],capture_output=True,text=True,encoding='utf-8',timeout=120)
        result=load(path) if proc.returncode==0 and path.exists() else {'program_id':row['program_id'],'valid':False,'error':'WorkerFailure: '+proc.stderr[-2000:],'instances':[]}
    except subprocess.TimeoutExpired:result={'program_id':row['program_id'],'valid':False,'error':'Worker timeout120s','instances':[]}
    result['subprocess_wall_seconds']=time.perf_counter()-start;save(path,result);return result

def extract():
    check_lock('extraction_lock.json');assert load(ROOT/'extraction/calibration_gate.json')['passed'];rows=[r for r in load(ROOT/'sources/program_registry.json') if r['convertible']]
    (ROOT/'extraction/results').mkdir(exist_ok=True)
    start=time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures={pool.submit(dispatch,row):row for row in rows}
        for i,future in enumerate(concurrent.futures.as_completed(futures),1):
            result=future.result()
            if i%25==0 or i==len(rows):print('paired full-packing checks',i,'/',len(rows),'last_valid',result['valid'],flush=True)
    save(ROOT/'extraction/evaluation_complete.json',{'completed_at':c.now(),'evaluated_programs':len(rows),'this_session_wall_seconds':time.perf_counter()-start,'LLM_requests':0})
    catalog()

def catalog():
    check_lock('extraction_lock.json');programs=load(ROOT/'sources/program_registry.json');raw={};clean={};coverage=[]
    for row in programs:
        result=load(ROOT/'extraction/results'/f"{row['program_id']}.json") if row['convertible'] else {}
        accepted=bool(result.get('valid'));coverage.append({'program_id':row['program_id'],'origins':len(row['origins']),
            'static_convertible':row['convertible'],'exact_score_and_full_packing_verified':accepted,
            'probe_comparisons':result.get('probe_score_comparisons',0),'packing_score_comparisons':result.get('packing_state_score_comparisons',0),
            'nonfinite_probe_outputs':result.get('nonfinite_probe_outputs',0),'pilot_dev_mean':result.get('mean_bins'),
            'error':row.get('error') or result.get('error','')})
        if not accepted:continue
        expression=t.parse(row['expression'])
        for path,node,kind in t.locations(expression):
            k=t.key(node);normal=t.canonical(node);nk=t.key(normal)
            source={'program_id':row['program_id'],'expanded_path':list(path),'source_line':getattr(node,'lineno',None),'origin_multiplicity':max(1,len(row['origins']))}
            if k not in raw:raw[k]={'key':k,'expression':t.text(node),'type':kind,'size':t.size(node),'depth':t.depth(node),
                'terminal_dependencies':sorted({n.id for n in ast.walk(node) if isinstance(n,ast.Name) and n.id in {'bins','item'}}),
                'module_dependencies':['numpy as np'] if any(isinstance(n,ast.Name) and n.id=='np' for n in ast.walk(node)) else [],
                'sources':[], 'occurrence_weight':0}
            raw[k]['sources'].append(source);raw[k]['occurrence_weight']+=source['origin_multiplicity']
            if nk not in clean:clean[nk]={'key':nk,'expression':t.text(normal),'type':t.infer(normal),'size':t.size(normal),'depth':t.depth(normal),
                'terminal_dependencies':sorted({n.id for n in ast.walk(normal) if isinstance(n,ast.Name) and n.id in {'bins','item'}}),
                'module_dependencies':['numpy as np'] if any(isinstance(n,ast.Name) and n.id=='np' for n in ast.walk(normal)) else [],
                'raw_keys':[],'sources':[]}
            if k not in clean[nk]['raw_keys']:clean[nk]['raw_keys'].append(k)
            clean[nk]['sources'].append(source)
    save(ROOT/'extraction/raw_fragments.json',list(raw.values()));save(ROOT/'extraction/clean_fragments.json',list(clean.values()))
    c.table(ROOT/'extraction/program_coverage.csv',coverage)
    merged=sum(len(r['raw_keys'])>1 for r in clean.values())
    timings=[load(p) for p in (ROOT/'extraction/results').glob('*.json')]
    runtime=[sum(i['expanded_runtime'] for i in r['instances']) for r in timings if r['valid']]
    summary={'completed_at':c.now(),'LLM_requests':0,'source_unique_programs':len(programs),
        'source_origin_records':sum(len(r['origins']) for r in programs),'static_convertible_programs':sum(r['convertible'] for r in programs),
        'verified_full_packing_programs':sum(r['exact_score_and_full_packing_verified'] for r in coverage),
        'program_coverage_rate':sum(r['exact_score_and_full_packing_verified'] for r in coverage)/len(programs),
        'raw_unique_structural_fragments':len(raw),'raw_fragment_occurrences_weighted':sum(r['occurrence_weight'] for r in raw.values()),
        'clean_unique_structural_fragments':len(clean),'normalization_merging_groups':merged,
        'types_raw':dict(collections.Counter(r['type'] for r in raw.values())),
        'types_clean':dict(collections.Counter(r['type'] for r in clean.values())),
        'exclusion_reasons':dict(collections.Counter(r['error'] for r in coverage if not r['exact_score_and_full_packing_verified'])),
        'score_or_packing_mismatch_programs':[r['program_id'] for r in coverage if 'Mismatch' in r['error']],
        'all_source_scores_full_packing_equivalent_for_library':True,
        'five_instance_expanded_runtime_median':float(np.median(runtime)) if runtime else None,
        'five_instance_expanded_runtime_p95':float(np.quantile(runtime,.95)) if runtime else None,
        'worker_wall_seconds_sum':sum(r.get('subprocess_wall_seconds',0) for r in timings),
        'no_worst_fit_or_order_invariant_pruning':True,'finite_behavior_equivalence_not_used_for_dedup':True}
    save(ROOT/'extraction/summary.json',summary)
    print(json.dumps({k:summary[k] for k in ['source_unique_programs','static_convertible_programs','verified_full_packing_programs','raw_unique_structural_fragments','clean_unique_structural_fragments','score_or_packing_mismatch_programs','five_instance_expanded_runtime_median']},ensure_ascii=False),flush=True)

if __name__=='__main__':
    mode=sys.argv[1]
    if mode=='collect':collect()
    elif mode=='prepare':prepare()
    elif mode=='extract':extract()
    elif mode=='catalog':catalog()
    elif mode=='worker':extraction_worker(sys.argv[2],sys.argv[3])
    elif mode=='calibration':calibration()
    elif mode=='reference':reference_worker(sys.argv[2],sys.argv[3])
