"""Pre-launch checks use hand-written trees and synthetic states only."""
import os
for name in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[name]='1'
import collections,ctypes,importlib.util,json,subprocess,sys,time
from pathlib import Path
import equal_time as x
from process_control import Job
ROOT=x.ROOT

def helper(folder):
    child=subprocess.Popen([sys.executable,'-c','import time;time.sleep(60)'],creationflags=subprocess.CREATE_NO_WINDOW)
    x.save(folder/'descendant.json',{'pid':child.pid})
    # Nested candidate memory job must remain supervised by outer deadline job.
    np,g,t,c,prior,v=x.modules();x.save(folder/'nested_memory.json',c.memory_limit())
    time.sleep(60)

def alive(pid):
    from ctypes import wintypes
    k=ctypes.WinDLL('kernel32',use_last_error=True)
    k.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD];k.OpenProcess.restype=wintypes.HANDLE
    k.GetExitCodeProcess.argtypes=[wintypes.HANDLE,ctypes.POINTER(wintypes.DWORD)];k.GetExitCodeProcess.restype=wintypes.BOOL
    k.CloseHandle.argtypes=[wintypes.HANDLE]
    h=k.OpenProcess(0x1000,False,pid)
    if not h:return False
    code=wintypes.DWORD();k.GetExitCodeProcess(h,ctypes.byref(code));k.CloseHandle(h);return code.value==259

def main():
    assert not (ROOT/'execution_lock.json').exists(),'Cannot run prelaunch audit after execution lock'
    assert not (ROOT/'search_started.json').exists()
    np,g,t,c,prior,v=x.modules();checks={}
    folder=ROOT/'executor_checks'/str(time.time_ns());folder.mkdir(parents=True,exist_ok=False)
    # Handwritten packing cases and first-index ties through unchanged evaluator.
    fn=v.compile_score('def score(item, bins):\n    return -bins\n')
    for items,n in [([60,40,60,40],2),([51,49,50,50],2),([100,100],2)]:
        r,_,_=c.pack({'id':'synthetic','items':items,'num_items':len(items),'capacity':100},fn);assert r['bins_used']==n
    tied=v.compile_score('def score(item,bins):\n    return np.zeros_like(bins)\n')
    _,ix,_=c.pack({'id':'synthetic_tie','items':[60,60,40,40],'num_items':4,'capacity':100},tied);assert ix.tolist()==[0,1,0,1]
    checks['handwritten_packing_and_ties']=True
    assert g.limits(g.payload(t.parse('np.square(np.square(np.square(np.square(np.square(np.square(np.square(np.square(bins))))))))')))
    checks['expanded_limits']=True
    for block in range(3):
        seq=[x.schedule_operator(np,g,12345,block*112+i) for i in range(1,113)]
        assert collections.Counter(seq)=={'crossover':56,'subtree_replace':39,'constant_mutation':17}
    checks['operator_quota_and_unbounded_blocks']=True
    parent={'id':'synthetic_parent','mean_bins':2066.4,**g.payload(t.parse('np.maximum(-(bins-item), -np.square(bins-item))'))}
    # A hand-written proper fragment, independent of research-seed outcomes.
    node=t.parse('np.abs(bins-item)+item');library={k:[(t.parse('item') if k=='S' else node if k=='V' else t.parse('item>0') if k=='BS' else t.parse('bins>item'),'synthetic_fragment')] for k in ['S','V','BS','BV']}
    plans=[]
    for attempt in range(1,101):
        m,rs,p=x.proposal(12345,attempt,[parent],library,g,t,np,op='subtree_replace')
        if m['eligible_position_mechanism'] and len([r for r in rs if r['structure_legal']])>=2:
            plans.append((attempt,m,rs,p))
    assert plans
    vocab=x.load(ROOT/'frozen/operator_vocabulary.json')
    models={m:x.load(ROOT/'frozen'/f)['model'] for m,f in [('structure_position_gp','frozen_structure_ranker.json'),('behavior_A_position_gp','frozen_behavior_A_ranker.json')]}
    synthetic=[]
    for i in range(64):
        a=np.asarray([20+i%4,30+i%7,60+i%3],dtype=np.float64);a.setflags(write=False)
        synthetic.append({'state_id':f'synthetic_{i}','item':10+i%8,'array':a})
    fixture=plans[0]
    choice_ids={};counter_keys=['probe_cache_state_hits','probe_cache_state_misses','probe_seconds','ranking_seconds','rankable_proposals','rankable_parent_better','rankable_parent_equal','rankable_parent_worse','choice_differs_from_uniform']
    for method in ['uniform_position_gp','structure_position_gp','behavior_A_position_gp']:
        attempt,meta,variants,p=fixture
        # Fresh same proposal for each method, then only selector may differ.
        m,rs,p=x.proposal(12345,attempt,[parent],library,g,t,np,op='subtree_replace')
        assert x.digest([m,rs])==x.digest([meta,variants])
        counters=dict.fromkeys(counter_keys,0);cache={}
        chosen=x.choose(12345,attempt,method,m,rs,p,models,vocab,synthetic,'synthetic_pool',cache,time.perf_counter()+10,np,g,t,v,counters)
        assert chosen and chosen['structure_legal'];choice_ids[method]=chosen['trial_index']
        if method=='behavior_A_position_gp':
            before=counters['probe_cache_state_misses'];x.get_probes(p,cache,synthetic,'synthetic_pool',time.perf_counter()+10,np,g,t,v,counters)
            assert counters['probe_cache_state_misses']==before and counters['probe_cache_state_hits']>=64
    checks['method_independent_trials_and_cold_cache']=True
    # Exact feature and inference compatibility against frozen source functions.
    spec=importlib.util.spec_from_file_location('audit_frozen_reference',ROOT.parent/'fragment_position_ranking_explore_01/explore.py')
    e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)
    for row in fixture[2]:
        row.update(A_valid=61,A_paired_valid=60,A_all_equal=3,A_changed=17)
        for model in models.values():
            assert np.array_equal(x.features(np,row,vocab,model['behavior']),e.features(row,model['behavior'],'A'))
            assert x.rank_score(np,model,row,vocab)==e.score(model,row,'A')
        assert x.tie(row)==e.tie(row)
    checks['frozen_features_scores_and_ties_exact']=True
    # Snapshot exists before marker, expired state never receives a commit marker.
    commit_folder=folder/'commit_fixture';commit_folder.mkdir(exist_ok=True)
    x.commit(commit_folder,{'commits':0,'synthetic':True},time.perf_counter()+2)
    assert len(list((commit_folder/'commits').glob('*.commit')))==1
    try:x.commit(commit_folder,{'commits':1},time.perf_counter()-.1)
    except x.Cutoff:pass
    else:raise AssertionError('Expired commit accepted')
    assert len(list((commit_folder/'commits').glob('*.commit')))==1
    checks['deadline_commits_and_reject_expired']=True
    binary=subprocess.run([sys.executable,'-c',"import sys;sys.stderr.buffer.write(bytes([164,165,255]));sys.exit(7)"],capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW)
    assert binary.returncode==7 and binary.stderr==bytes([164,165,255])
    assert (binary.stderr or b'').decode('utf-8',errors='replace')
    checks['non_utf8_failed_worker_stderr_preserved_without_reader_crash']=True
    # Reproduce OneDrive-style deny-delete handle on an existing JSON target.
    import threading
    locked=folder/'locked_result.json';x.save(locked,{'version':0})
    handle,k=deny_delete(locked)
    release=threading.Timer(.25,lambda:k.CloseHandle(handle));release.start();start=time.perf_counter()
    x.save(locked,{'version':1});duration=time.perf_counter()-start;release.join()
    assert x.load(locked)=={'version':1} and duration>=.20
    for i in range(50):x.save(locked,{'version':i,'payload':list(range(100))})
    assert x.load(locked)['version']==49
    checks['atomic_write_retries_real_deny_delete_lock']=True
    late=commit_folder/'commits/000002.json';x.save(late,{'synthetic_previous':True})
    handle,k=deny_delete(late)
    release=threading.Timer(.25,lambda:k.CloseHandle(handle));release.start()
    try:x.commit(commit_folder,{'commits':1,'synthetic_retry_over_deadline':True},time.perf_counter()+.05)
    except x.Cutoff:pass
    else:raise AssertionError('I/O retry promoted a late result')
    release.join();assert not late.with_suffix('.commit').exists()
    checks['IO_retry_is_paid_and_late_commit_rejected']=True
    job=Job();start=time.perf_counter()
    proc=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'helper',str(folder)],creationflags=subprocess.CREATE_NO_WINDOW)
    job.assign(proc)
    until=start+8
    while time.perf_counter()<until and not (folder/'nested_memory.json').exists():time.sleep(.02)
    assert (folder/'nested_memory.json').exists() and x.load(folder/'nested_memory.json')['enforced']
    descendant=x.load(folder/'descendant.json')['pid'];assert alive(descendant)
    job.terminate();proc.wait(timeout=5);job.close();time.sleep(.1)
    assert not alive(descendant) and proc.poll() is not None
    checks['watchdog_kills_descendants_with_nested_memory_job']=True
    x.save(ROOT/'execution_environment.json',{'at':x.now(),'OS':platform_info(),'python':sys.version,'executable':sys.executable,'numpy':np.__version__,
        'logical_cpus':os.cpu_count(),'cpu':cpu_info(),
        'simultaneous_runs':1,'candidate_workers':1,'blas_threads':1,'affinity':affinity_info(),
        'resource_limit':x.load(folder/'nested_memory.json')})
    x.save(ROOT/'executor_audit.json',{'at':x.now(),'passed':all(checks.values()),'checks':checks,'synthetic_rankable_fixtures':len(plans),'example_selected_trial_indices':choice_ids,
        'new_research_searches':0,'new_research_packing_evaluations':0,'synthetic_only_packing_cases':4,'new_LLM_calls':0,'no_fit_called':True})
    print(json.dumps(x.load(ROOT/'executor_audit.json')),flush=True)

def platform_info():
    import platform
    return platform.platform()
def affinity_info():
    from ctypes import wintypes
    k=ctypes.WinDLL('kernel32',use_last_error=True)
    k.GetCurrentProcess.restype=wintypes.HANDLE
    k.GetProcessAffinityMask.argtypes=[wintypes.HANDLE,ctypes.POINTER(ctypes.c_size_t),ctypes.POINTER(ctypes.c_size_t)]
    a=ctypes.c_size_t();b=ctypes.c_size_t()
    assert k.GetProcessAffinityMask(k.GetCurrentProcess(),ctypes.byref(a),ctypes.byref(b))
    return {'pinning':'OS default','process_mask':hex(a.value),'system_mask':hex(b.value)}
def cpu_info():
    import winreg
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,r'HARDWARE\DESCRIPTION\System\CentralProcessor\0') as key:
        return {'name':winreg.QueryValueEx(key,'ProcessorNameString')[0],'vendor':winreg.QueryValueEx(key,'VendorIdentifier')[0]}
def deny_delete(path):
    from ctypes import wintypes
    k=ctypes.WinDLL('kernel32',use_last_error=True)
    k.CreateFileW.argtypes=[wintypes.LPCWSTR,wintypes.DWORD,wintypes.DWORD,ctypes.c_void_p,wintypes.DWORD,wintypes.DWORD,wintypes.HANDLE]
    k.CreateFileW.restype=wintypes.HANDLE;k.CloseHandle.argtypes=[wintypes.HANDLE]
    handle=k.CreateFileW(str(path),0x80000000,3,None,3,0x80,None)
    assert handle not in [None,ctypes.c_void_p(-1).value]
    return handle,k
if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='helper':helper(Path(sys.argv[2]))
    else:main()
