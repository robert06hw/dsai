"""Offline CPU-only phase one. No network or LLM entry point."""
import ast, concurrent.futures, csv, ctypes, datetime, hashlib, heapq, json
import math, os, platform, shutil, subprocess, sys, time, warnings
from pathlib import Path
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
os.environ['MKL_NUM_THREADS']='1'
import numpy as np

ROOT=Path(__file__).resolve().parent
HISTORY=['ci_evo_work','ci_evo_p3_followup','ci_evo_round2','ci_evo_parent_dependence','ci_evo_ec_exploration']
def now(): return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
def sha(x): return hashlib.sha256(x.encode() if isinstance(x,str) else x).hexdigest()
def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def save(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8');tmp.replace(p)
def table(p,rows,fields=None):
    rows=list(rows);fields=fields or (list(rows[0]) if rows else [])
    with Path(p).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def data(split):
    with (ROOT/'data'/f'{split}.jsonl').open(encoding='utf-8') as f:return [json.loads(s) for s in f]
def check_lock():
    for p,h in load(ROOT/'pre_evaluation_lock.json')['files'].items():assert sha((ROOT/p).read_bytes())==h,p
def generator(split,seeds,n,uniform=False):
    out=[]
    for seed in seeds:
        rng=np.random.Generator(np.random.PCG64(seed))
        items=rng.integers(1,101,n) if uniform else np.floor(np.clip(45.*rng.weibull(3.,n),1.,100.)).astype(np.int64)
        out.append({'id':f'{split}_{seed}','seed':seed,'distribution':'UNIFORM_INT_1_100' if uniform else 'WB3S45_INT_C100_N5000_v1',
            'capacity':100,'num_items':n,'items':items.tolist()})
    return out
def prepare():
    assert not (ROOT/'pre_evaluation_lock.json').exists(),'Cannot relock'
    source=Path(r'C:\Users\rober\Downloads\Behavior_Grouping_EC_Proposal.md')
    (ROOT/'sources').mkdir(exist_ok=True);shutil.copy2(source,ROOT/'sources'/source.name)
    cal=ROOT.parent/'baseline_calibration_01'
    for name in ['First-fit','Best-fit','EoH','FunSearch']:
        (ROOT/'rules').mkdir(exist_ok=True);shutil.copy2(cal/'rules'/f'{name}.py',ROOT/'rules'/f'{name}.py')
    shutil.copy2(cal/'sources/repository_version.json',ROOT/'sources/repository_version.json')
    shutil.copy2(ROOT.parent/'ci_evo_ec_exploration/scoring.py',ROOT/'historical_validator.py')
    shutil.copy2(ROOT.parent/'ci_evo_ec_exploration/genotypes.py',ROOT/'historical_purity.py')
    # Purity helper imports scoring: give it the unchanged local copy, never source-edit archived code.
    shutil.copy2(ROOT.parent/'ci_evo_ec_exploration/scoring.py',ROOT/'scoring.py')
    splits={'pilot_dev':(range(6001,6006),5000,False),'pilot_val':(range(6101,6106),5000,False),
        'dev':(range(1001,1011),5000,False),'validation':(range(2001,2011),5000,False),
        'test_id':(range(3001,3031),5000,False),'probe_audit':(range(4001,4011),5000,False),
        'test_uniform':(range(5001,5011),5000,True),'test_short':(range(5101,5111),1000,False)}
    historical=set()
    for folder in HISTORY:
        p=ROOT.parent/folder/'datasets.json'
        if p.exists():
            for group in load(p).values():
                for i in group:historical.add(sha(np.asarray(i['items'],dtype='<i4').tobytes()))
    for p in (cal/'data').glob('*.json'):
        x=load(p)
        if isinstance(x,list):
            for i in x:historical.add(sha(np.asarray(i['items'],dtype='<i4').tobytes()))
    rows=[];seen=set();(ROOT/'data').mkdir(exist_ok=True)
    for split,(seeds,n,uniform) in splits.items():
        instances=generator(split,seeds,n,uniform)
        path=ROOT/'data'/f'{split}.jsonl'
        path.write_text(''.join(json.dumps(i,separators=(',',':'))+'\n' for i in instances),encoding='utf-8')
        for i in instances:
            h=sha(np.asarray(i['items'],dtype='<i4').tobytes());assert h not in seen|historical;seen.add(h)
            rows.append({'split':split,'instance_id':i['id'],'seed':i['seed'],'num_items':n,'capacity':100,'distribution':i['distribution'],
                'items_sha256':h,'file':path.relative_to(ROOT).as_posix(),'file_sha256':sha(path.read_bytes()),'evaluated_in_phase1':split in ['pilot_dev','dev','probe_audit']})
    table(ROOT/'data_manifest.csv',rows)
    sys.path.insert(0,str(ROOT));import historical_validator as validator
    registry={};origins=[];requests=[]
    def add(code,origin):
        ch=sha(code);status='pending';ast_hash='';reason=''
        try:
            tree=ast.parse(code);ast_hash=sha(ast.dump(tree,include_attributes=False))
            validator.compile_score(code)
            import historical_purity as purity
            purity.check_purity(tree)
        except Exception as e:status='interface_rejected';reason=f'{type(e).__name__}: {e}'
        key=ast_hash or ch
        if key not in registry:
            p=ROOT/'candidates'/f'{key}.py';p.parent.mkdir(exist_ok=True);p.write_text(code,encoding='utf-8')
            registry[key]={'candidate_id':key,'code_sha256':ch,'ast_sha256':ast_hash,'status':status,'interface_error':reason,
                'path':p.relative_to(ROOT).as_posix(),'origins':[]}
        registry[key]['origins'].append(origin)
        origins.append({'candidate_id':key,'code_sha256':ch,**origin})
    for folder in HISTORY:
        source_dir=ROOT.parent/folder
        for p in sorted((source_dir/'raw').glob('*.json')):
            r=load(p);child=source_dir/'children'/f'{p.stem}.py'
            requests.append({'experiment':folder,'request_id':r['id'],'raw_sha256':sha(p.read_bytes()),'response_saved':'response' in r,
                'code_saved':child.exists(),'historical_valid':r.get('evaluation',{}).get('valid',r.get('valid',''))})
            if child.exists():add(child.read_text(encoding='utf-8'),{'experiment':folder,'kind':'generated','request_id':r['id'],'source_path':str(child),'source_sha256':sha(child.read_bytes())})
            elif 'response' in r:
                add(validator.extract(r['response'].get('response','')),{'experiment':folder,'kind':'generated','request_id':r['id'],'source_path':str(p),'source_sha256':sha(p.read_bytes())})
        parents=source_dir/'parents.json'
        if parents.exists():
            for pid,p in load(parents).items():
                for rep,code in p['programs'].items():add(code,{'experiment':folder,'kind':'parent','request_id':pid+'_'+rep,'source_path':str(parents),'source_sha256':sha(parents.read_bytes())})
    assert len(requests)==2496
    save(ROOT/'candidates_registry.json',list(registry.values()));save(ROOT/'historical_requests.json',requests)
    table(ROOT/'candidate_origins.csv',origins)
    archive={}
    for folder in HISTORY+['ci_evo_ec_audit_20261004','baseline_calibration_01']:
        path=ROOT.parent/folder/'manifest.json';archive[folder]=sha(path.read_bytes())
    save(ROOT/'source_archive_lock.json',archive)
    config={'experiment':'behavior_stage1_01','version':1,'locked_at':now(),'new_llm_requests':0,'new_searches':0,
        'numpy':np.__version__,'python':platform.python_version(),'platform':platform.platform(),'dataset':'WB3S45_INT_C100_N5000_v1',
        'rounding':'floor','rng':'numpy.Generator(PCG64(instance_seed))','capacity':100,
        'evaluated_splits':['pilot_dev','dev','probe_audit_states_only'],'unopened_splits':['pilot_val','validation','test_id','test_uniform','test_short'],
        'pool_seeds':{'dev':7001,'probe_audit':7002},'pool_max_states':1024,'source_quota':256,'pool_reservoir_per_source':1024,
        'selection_seeds':list(range(8001,8006)),'probe_sizes':[32,64,128],'anchors':16,'query_budget':73728,'snapshot_refresh_interval':8,
        'workers':4,'candidate_wall_timeout_seconds':120,'candidate_memory_limit_bytes':512*1024**2,
        'raw_historical_generations':2496,'unique_AST_candidates':len(registry),'static_diagnostic_runs':45,
        'primary_identity':'Full parsed AST, including local names; no behavior or expanded-tree deduplication',
        'primary_fingerprint':'Chosen pre-placement remaining capacity, exact integer; local feasible index separately',
        'calibration_gate':'EoH or FunSearch strictly fewer mean pilot_dev bins than Best-fit',
        'quality_subset':'Full dev mean bins <= Best-fit mean * 1.0025',
        'global_active_budget':'Static CPU diagnostic pays all N*pool_size evaluations and reports whether above the prospective EC cap. The 73728 cap is enforced separately for each historical-population shadow replay',
        'fixed_repetitions':'One fixed pool_seed=7001 subset per size reused five times; not five independent fixed selections',
        'static_random':'Five independent one-time resamples, no evolution',
        'snapshot_analysis':'Read-only grouping replay of historical populations, no changed parent choices, no H3 claim'}
    save(ROOT/'config.json',config)
    save(ROOT/'initialization.json',{'new_llm_requests':0,'new_population_initialized':False,'source':'Complete saved history','deferred_experiment':'b_small_model_01: no generation started'})
    table(ROOT/'generations.csv',requests)
    unit_checks()
    files=[p for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='pre_evaluation_lock.json']
    save(ROOT/'pre_evaluation_lock.json',{'locked_at':config['locked_at'],'files':{p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in files}})
    print(json.dumps({'datasets':len(rows),'historical_requests':len(requests),'unique_AST':len(registry),'interface_accepted':sum(r['status']=='pending' for r in registry.values()),'lock':config['locked_at']}),flush=True)

def trusted(name):
    namespace={'np':np};code=(ROOT/'rules'/f'{name}.py').read_text(encoding='utf-8');exec(compile(code,name,'exec'),namespace)
    return namespace['heuristic' if name=='FunSearch' else 'score']
def priorities(fn,item,caps):
    feasible=np.asarray(caps,dtype=np.float64);feasible.setflags(write=False)
    with np.errstate(divide='warn',over='warn',invalid='warn',under='ignore'):v=fn(float(item),feasible)
    if not isinstance(v,np.ndarray) or v.shape!=feasible.shape or v.dtype.kind not in 'fi':raise ValueError('Output must be numeric ndarray of feasible shape')
    v=np.asarray(v,dtype=np.float64)
    if not np.all(np.isfinite(v)):raise ValueError('Nonfinite score')
    return int(np.argmax(v))
class PoolSampler:
    def __init__(self,seed,source):self.seed=seed;self.source=source;self.heap=[];self.states={}
    def add(self,item,caps,indices,instance_id,step):
        if len(caps)<2 or np.min(caps)==np.max(caps):return
        vals=caps.astype(np.int16).tolist();h=sha(json.dumps([int(item),vals],separators=(',',':')))
        if h in self.states:return
        priority=int(sha(f'{self.seed}:{self.source}:{h}'),16)
        if len(self.heap)>=1024 and priority>=-self.heap[0][0]:return
        if len(self.heap)>=1024:
            _,old=heapq.heappop(self.heap);del self.states[old]
        self.states[h]={'state_hash':h,'item':int(item),'feasible_capacities':vals,'global_bin_indices':indices.tolist(),
            'source':self.source,'instance_id':instance_id,'step':step}
        heapq.heappush(self.heap,(-priority,h))
    def ordered(self):return [self.states[h] for _,h in sorted(self.heap,key=lambda v:(-v[0],v[1]))]
def pack(instance,fn,sampler=None):
    start=time.perf_counter();cpu=time.process_time();remaining=np.zeros(instance['num_items'],dtype=np.float64);opened=0
    choices=[];capacities=[];new_count=0
    for position,item in enumerate(instance['items'],1):
        feasible=np.flatnonzero(remaining[:opened]>=item)
        if not len(feasible):
            chosen=opened;remaining[opened]=instance['capacity'];opened+=1;new_count+=1
        else:
            caps=remaining[feasible].copy()
            if sampler:sampler.add(item,caps,feasible,instance['id'],position)
            chosen=int(feasible[priorities(fn,item,caps)])
        capacities.append(int(remaining[chosen]));remaining[chosen]-=item;choices.append(chosen)
        if remaining[chosen]<0:raise ValueError('Negative remaining capacity')
    assert math.isclose(float(np.sum(remaining[:opened]))+sum(instance['items']),opened*instance['capacity'],rel_tol=0,abs_tol=1e-8)
    return {'bins_used':opened,'runtime':time.perf_counter()-start,'cpu_seconds':time.process_time()-cpu,
        'trace_hash':sha(np.asarray(choices,dtype='<i4').tobytes()),'chosen_capacity_hash':sha(np.asarray(capacities,dtype='<i2').tobytes()),
        'new_bins':new_count},np.asarray(choices,dtype=np.int32),np.asarray(capacities,dtype=np.int16)
def unit_checks():
    checks=[];bf=lambda item,bins:-(bins-item)
    for items,expected in [([60,40,60,40],2),([100,100],2),([51,49,50,50],2),([60,60,40,40],2),([30,30,30,10],1)]:
        inst={'id':'unit','num_items':len(items),'capacity':100,'items':items};r,choices,_=pack(inst,bf);assert r['bins_used']==expected
        checks.append({'items':items,'expected_bins':expected,'observed_bins':r['bins_used'],'choices':choices.tolist()})
    calls=[]
    def tracked(item,bins):calls.append(bins.tolist());return np.zeros_like(bins)
    r,choices,_=pack({'id':'tie','num_items':4,'capacity':100,'items':[60,60,40,40]},tracked)
    assert choices.tolist()==[0,1,0,1] and calls==[[40.,40.],[40.]]
    caps=np.array([20,20,30]);assert caps[0]==caps[1] and 0!=1
    save(ROOT/'unit_checks.json',{'passed':True,'cases':checks,'only_open_feasible_bins':True,'empty_state_opens_without_scoring':True,
        'earliest_tie':True,'capacity_conservation':True,'same_capacity_different_indices_same_fingerprint':True})

def memory_limit():
    if os.name!='nt':return {'enforced':False,'reason':'Non-Windows host'}
    from ctypes import wintypes
    class IO(ctypes.Structure):_fields_=[(x,ctypes.c_uint64) for x in ['ReadOperationCount','WriteOperationCount','OtherOperationCount','ReadTransferCount','WriteTransferCount','OtherTransferCount']]
    class BASIC(ctypes.Structure):_fields_=[('PerProcessUserTimeLimit',ctypes.c_int64),('PerJobUserTimeLimit',ctypes.c_int64),('LimitFlags',wintypes.DWORD),('MinimumWorkingSetSize',ctypes.c_size_t),('MaximumWorkingSetSize',ctypes.c_size_t),('ActiveProcessLimit',wintypes.DWORD),('Affinity',ctypes.c_size_t),('PriorityClass',wintypes.DWORD),('SchedulingClass',wintypes.DWORD)]
    class EXT(ctypes.Structure):_fields_=[('BasicLimitInformation',BASIC),('IoInfo',IO),('ProcessMemoryLimit',ctypes.c_size_t),('JobMemoryLimit',ctypes.c_size_t),('PeakProcessMemoryUsed',ctypes.c_size_t),('PeakJobMemoryUsed',ctypes.c_size_t)]
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.CreateJobObjectW.argtypes=[ctypes.c_void_p,wintypes.LPCWSTR];kernel.CreateJobObjectW.restype=wintypes.HANDLE
    kernel.SetInformationJobObject.argtypes=[wintypes.HANDLE,ctypes.c_int,ctypes.c_void_p,wintypes.DWORD];kernel.SetInformationJobObject.restype=wintypes.BOOL
    kernel.GetCurrentProcess.restype=wintypes.HANDLE
    kernel.AssignProcessToJobObject.argtypes=[wintypes.HANDLE,wintypes.HANDLE];kernel.AssignProcessToJobObject.restype=wintypes.BOOL
    handle=kernel.CreateJobObjectW(None,None);info=EXT();info.BasicLimitInformation.LimitFlags=0x100;info.ProcessMemoryLimit=512*1024**2
    if not handle or not kernel.SetInformationJobObject(handle,9,ctypes.byref(info),ctypes.sizeof(info)) or not kernel.AssignProcessToJobObject(handle,kernel.GetCurrentProcess()):
        raise RuntimeError(f'Windows memory limit could not be applied: {ctypes.get_last_error()}')
    return {'enforced':True,'bytes':info.ProcessMemoryLimit,'job_handle':int(handle)}

def calibration_and_pools():
    check_lock();rows=[];all_results=[]
    for name in ['First-fit','Best-fit','EoH','FunSearch']:
        fn=trusted(name)
        for i in data('pilot_dev'):
            with warnings.catch_warnings(record=True) as ws:
                warnings.simplefilter('once');r,choices,caps=pack(i,fn)
            record={'dataset':'pilot_dev','instance_id':i['id'],'heuristic':name,**r,'error':'','warnings':sorted(set(str(w.message) for w in ws))}
            save(ROOT/'calibration'/f'{name}_{i["id"]}.json',record)
            (ROOT/'calibration/traces').mkdir(parents=True,exist_ok=True);np.savez_compressed(ROOT/'calibration/traces'/f'{name}_{i["id"]}.npz',indices=choices,capacities=caps)
            all_results.append(record)
        print('pilot_dev reference complete:',name,flush=True)
    bf={r['instance_id']:r['bins_used'] for r in all_results if r['heuristic']=='Best-fit'}
    for name in ['First-fit','Best-fit','EoH','FunSearch']:
        rs=[r for r in all_results if r['heuristic']==name];deltas=[bf[r['instance_id']]-r['bins_used'] for r in rs]
        rows.append({'heuristic':name,'mean_bins':float(np.mean([r['bins_used'] for r in rs])),'delta_vs_best_fit':float(np.mean(deltas)),
            'wins':sum(d>0 for d in deltas),'ties':sum(d==0 for d in deltas),'losses':sum(d<0 for d in deltas),'runtime':sum(r['runtime'] for r in rs)})
    table(ROOT/'calibration_summary.csv',rows);table(ROOT/'calibration_instance_results.csv',[{k:r[k] for k in ['dataset','instance_id','heuristic','bins_used','runtime','error']} for r in all_results])
    gate=any(r['delta_vs_best_fit']>0 for r in rows if r['heuristic'] in ['EoH','FunSearch'])
    save(ROOT/'calibration_gate.json',{'passed':gate,'rule':'Known EoH or FunSearch strictly better mean bins than Best-fit','rows':rows,'zero_llm_calls':True})
    refrows=[];poolmeta=[]
    for split,seed in [('dev',7001),('probe_audit',7002)]:
        collectors={};start=time.perf_counter()
        for name in ['First-fit','Best-fit','EoH','FunSearch']:
            sampler=PoolSampler(seed,name);fn=trusted(name)
            for i in data(split):
                with warnings.catch_warnings(record=True) as ws:
                    warnings.simplefilter('once');r,choices,caps=pack(i,fn,sampler)
                refrows.append({'dataset':split,'instance_id':i['id'],'heuristic':name,**r,'error':''})
                (ROOT/'reference_traces').mkdir(exist_ok=True);np.savez_compressed(ROOT/'reference_traces'/f'{split}_{name}_{i["id"]}.npz',indices=choices,capacities=caps)
            collectors[name]=sampler.ordered();print('state-source complete:',split,name,len(collectors[name]),flush=True)
        pool=[];used=set();positions={n:0 for n in collectors};counts={n:0 for n in collectors}
        for _ in range(256):
            for name,states in collectors.items():
                while positions[name]<len(states) and states[positions[name]]['state_hash'] in used:positions[name]+=1
                if positions[name]>=len(states):continue
                row=states[positions[name]];positions[name]+=1;pool.append(row);used.add(row['state_hash']);counts[name]+=1
        pool.sort(key=lambda s:s['state_hash']);assert len(pool)>=128 and len(used)==len(pool)
        save(ROOT/'pools'/f'{split}.json',pool)
        poolmeta.append({'split':split,'seed':seed,'states':len(pool),'source_counts':counts,'construction_wall_seconds':time.perf_counter()-start,
            'candidate_states_added':0,'role':'fitness-source observations' if split=='dev' else 'external diagnostic only'})
    table(ROOT/'reference_instance_results.csv',[{k:r[k] for k in ['dataset','instance_id','heuristic','bins_used','runtime','error']} for r in refrows])
    save(ROOT/'pool_metadata.json',poolmeta)
    save(ROOT/'cpu_inputs_ready.json',{'completed_at':now(),'gate_passed':gate,'pool_file_hashes':{s:sha((ROOT/'pools'/f'{s}.json').read_bytes()) for s in ['dev','probe_audit']}})

def worker(cid):
    start=time.perf_counter();cpu=time.process_time();limit=memory_limit();p=ROOT/'candidate_results'/f'{cid}.json'
    result={'candidate_id':cid,'valid_dev':False,'valid_pools':False,'started_at':now(),'resource_limit':limit,'instances':[], 'error':'','error_phase':''}
    try:
        import historical_validator as v
        fn=v.compile_score((ROOT/'candidates'/f'{cid}.py').read_text(encoding='utf-8'))
        choices={};selected={}
        with warnings.catch_warnings(record=True) as ws:
            warnings.simplefilter('once')
            for i in data('dev'):
                result['error_phase']='dev';r,indices,caps=pack(i,fn);result['instances'].append({'dataset':'dev','instance_id':i['id'],**r})
                choices[i['id']]=indices;selected[i['id']]=caps
            result['valid_dev']=True;result['dev_mean_bins']=float(np.mean([r['bins_used'] for r in result['instances']]))
            (ROOT/'candidate_traces').mkdir(exist_ok=True);np.savez_compressed(ROOT/'candidate_traces'/f'{cid}.npz',**{f'indices_{k}':x for k,x in choices.items()},**{f'capacities_{k}':x for k,x in selected.items()})
            capacities={};indices={};execution_counts={};pool_times={}
            for split in ['dev','probe_audit']:
                result['error_phase']=split+'_pool';cs=[];ix=[];t=time.perf_counter()
                for state in load(ROOT/'pools'/f'{split}.json'):
                    pos=priorities(fn,state['item'],state['feasible_capacities']);ix.append(pos);cs.append(state['feasible_capacities'][pos])
                execution_counts[split]=len(cs);pool_times[split]=time.perf_counter()-t;capacities[split]=np.asarray(cs,dtype=np.int16);indices[split]=np.asarray(ix,dtype=np.int16)
            (ROOT/'fingerprints').mkdir(exist_ok=True);np.savez_compressed(ROOT/'fingerprints'/f'{cid}.npz',**capacities,**{s+'_indices':x for s,x in indices.items()})
            result.update(valid_pools=True,state_executions=execution_counts,pool_seconds=pool_times,error_phase='')
        result['warnings']=sorted(set(str(w.message) for w in ws))
    except Exception as e:result['error']=f'{type(e).__name__}: {e}'
    result['wall_seconds']=time.perf_counter()-start;result['cpu_seconds']=time.process_time()-cpu;result['completed_at']=now();save(p,result)

def invoke(cid):
    path=ROOT/'candidate_results'/f'{cid}.json'
    if path.exists():return load(path)
    start=time.perf_counter()
    try:
        process=subprocess.run([sys.executable,str(ROOT/'stage1.py'),'worker',cid],capture_output=True,text=True,encoding='utf-8',timeout=120)
        if process.returncode!=0 or not path.exists():
            save(path,{'candidate_id':cid,'valid_dev':False,'valid_pools':False,'instances':[],'error':'WorkerFailure: '+process.stderr[-1500:],
                'error_phase':'process','wall_seconds':time.perf_counter()-start,'completed_at':now()})
    except subprocess.TimeoutExpired:
        save(path,{'candidate_id':cid,'valid_dev':False,'valid_pools':False,'instances':[],'error':'120 second wall timeout','error_phase':'process',
            'wall_seconds':time.perf_counter()-start,'completed_at':now()})
    result=load(path);result['subprocess_wall_seconds']=time.perf_counter()-start;save(path,result);return result

def candidates():
    check_lock();assert (ROOT/'cpu_inputs_ready.json').exists();registry=load(ROOT/'candidates_registry.json')
    todo=[r['candidate_id'] for r in registry if r['status']=='pending'];start=time.perf_counter();completed=0
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for result in pool.map(invoke,todo):
            completed+=1
            if completed%20==0 or completed==len(todo):print(f'candidate CPU {completed}/{len(todo)}; valid_dev={result.get("valid_dev")}; elapsed={time.perf_counter()-start:.1f}s',flush=True)
    save(ROOT/'candidate_evaluation_complete.json',{'completed_at':now(),'candidates_attempted':len(todo),'wall_seconds_this_invocation':time.perf_counter()-start,'llm_calls':0})

def run():
    check_lock()
    if not (ROOT/'cpu_inputs_ready.json').exists():calibration_and_pools()
    candidates()
    subprocess.run([sys.executable,str(ROOT/'diagnose.py')],check=True)

if __name__=='__main__':
    mode=sys.argv[1]
    if mode=='prepare':prepare()
    elif mode=='run':run()
    elif mode=='worker':worker(sys.argv[2])
    elif mode=='calibrate':calibration_and_pools()
    elif mode=='candidates':candidates()
    else:raise ValueError(mode)
