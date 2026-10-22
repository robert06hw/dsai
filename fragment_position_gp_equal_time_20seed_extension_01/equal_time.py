"""Frozen equal-wall-time GP. Commands: lock, search, run-worker, fitness-worker.

No LLM or network code. Each run starts cold; all online work is inside its
scheduler deadline. Commit markers certify snapshots written before cutoff.
"""
import os
for name in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:
    os.environ[name]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
os.environ['PYTHONUTF8']='1'
os.environ['PYTHONIOENCODING']='utf-8'
import ast,collections,copy,csv,hashlib,json,math,platform,subprocess,sys,time,warnings
from pathlib import Path
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent
CORE=BASE/'fragment_gp_limited_01'
ASSETS=BASE/'dsai/assets'

def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    tmp=p.with_suffix(p.suffix+f'.{os.getpid()}.{time.time_ns()}.tmp')
    payload=json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)
    for attempt in range(30):
        try:
            tmp.write_text(payload,encoding='utf-8');break
        except PermissionError:
            if attempt==29:raise
            time.sleep(.05)
    for attempt in range(30):
        try:os.replace(tmp,p);return
        except PermissionError:
            if attempt==29:raise
            time.sleep(.05)
def now():
    import datetime
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
def modules():
    sys.path.insert(0,str(CORE))
    import numpy as np
    import gp_search as g
    import typed_tree as t
    import cpu as c
    import historical_prior as prior
    import historical_validator as v
    c.ROOT=ASSETS;prior.ROOT=CORE;g.ROOT=CORE
    return np,g,t,c,prior,v

class Cutoff(Exception):pass
def check(deadline):
    if time.perf_counter()>=deadline:raise Cutoff()

def schedule_operator(np,g,seed,attempt):
    block,index=divmod(attempt-1,112)
    seq=['crossover']*56+['subtree_replace']*39+['constant_mutation']*17
    g.rng(seed,block,102).shuffle(seq)
    return seq[index]

def proposal(seed,attempt,pop,library,g,t,np,op=None):
    """Method-independent RNG and trials. No ranking/fitness is read here."""
    op=op or schedule_operator(np,g,seed,attempt)
    parent=g.choice(pop,g.rng(seed,attempt,1));other=g.choice(pop,g.rng(seed,attempt,2))
    root=g.dec(parent['tree']);places=list(t.locations(root));path,old,kind=g.choice(places,g.rng(seed,attempt,3))
    meta={'operator':op,'parent_id':parent['id'],'parent_AST':parent['execution_key'],
          'parent_mean_bins':parent['mean_bins'],'second_parent_id':other['id'] if op=='crossover' else None,
          'anchor_path':list(path),'target_type':kind,'replacement_source':None,'fragment_key':None,'eligible_position_mechanism':False,'construction_error':''}
    try:
        paths=[path]
        if op=='crossover':
            donors=[(p,n) for p,n,k in t.locations(g.dec(other['tree'])) if k==kind]
            donor_path,donor=g.choice(donors,g.rng(seed,attempt,4));meta['donor_path']=list(donor_path)
        elif op=='subtree_replace':
            use_library=g.rng(seed,attempt,5).random()<.5
            if use_library:
                donor,key=g.choice(library[kind],g.rng(seed,attempt,6))
                meta.update(replacement_source='historical_fragment',fragment_key=key)
                if path and kind=='V':
                    meta['eligible_position_mechanism']=True
                    other_paths=sorted((p for p,n,k in places if p and k=='V' and p!=path),key=lambda p:json.dumps(list(p),separators=(',',':')))
                    picks=g.rng(seed,attempt,9).choice(len(other_paths),min(2,len(other_paths)),replace=False) if other_paths else []
                    paths=[path]+[other_paths[int(i)] for i in picks]
            else:
                r=g.rng(seed,attempt,6);donor=t.random_tree(kind,r,levels=int(r.integers(1,4)),safe=True)
                meta['replacement_source']='basic_operators'
        else:
            constants=[(p,n) for p,n,k in places if isinstance(n,ast.Constant) and isinstance(n.value,(float,int)) and not isinstance(n.value,bool)]
            path,old=g.choice(constants,g.rng(seed,attempt,7));value=float(old.value)+float(g.rng(seed,attempt,8).normal(0,5))
            paths=[path];meta.update(constant_before=old.value,constant_after=value)
            donor=ast.Constant(value=value)
        variants=[]
        location_nodes={p:n for p,n,k in places}
        for index,p in enumerate(paths):
            child=t.replace(root,p,donor);record=g.payload(child);err=g.limits(record)
            up=root
            for field,idx in p[:-1]:up=getattr(up,field) if idx is None else getattr(up,field)[idx]
            enclosing=type(up.op).__name__ if isinstance(up,(ast.BinOp,ast.UnaryOp)) else t.function_name(up.func) if isinstance(up,ast.Call) else type(up).__name__
            variants.append({'trial_index':index,'parent_AST':parent['execution_key'],'fragment_key':meta['fragment_key'],
                'target_path':list(p),'site_depth':len(p),'old_subtree_nodes':t.size(location_nodes[p]),
                'enclosing_operator':enclosing,**record,'structure_error':err,'structure_legal':not bool(err)})
        return meta,variants,parent
    except Exception as exc:
        meta['construction_error']=type(exc).__name__+': '+str(exc)
        return meta,[],parent

def features(np,row,vocab,behavior):
    op=row['enclosing_operator'] if row['enclosing_operator'] in vocab else '__OTHER__'
    xs=[row['site_depth'],math.log1p(row['old_subtree_nodes']),math.log1p(row['nodes']),row['depth']]+[float(op==s) for s in vocab]
    if behavior:
        changed=row['A_changed']/64
        xs += [row['A_valid']/64,row['A_paired_valid']/64,row['A_all_equal']/64,changed,changed*changed]
    return np.asarray(xs,dtype=float)
def rank_score(np,model,row,vocab):
    return float(np.dot(features(np,row,vocab,model['behavior'])/np.asarray(model['scale']),np.asarray(model['coefficients'])))
def tie(row):return digest([2026101803,row['parent_AST'],row['fragment_key'],row['target_path']])

def probe_one(np,fn,state):
    try:
        with np.errstate(all='ignore'):scores=fn(float(state['item']),state['array'])
        if not isinstance(scores,np.ndarray) or scores.shape!=state['array'].shape or scores.dtype.kind not in 'fi':raise ValueError('Output must be real numeric ndarray of feasible shape')
        if not np.all(np.isfinite(scores)):raise ValueError('Nonfinite score')
        return {'state_id':state['state_id'],'valid':True,'chosen_index':int(np.argmax(scores)),
            'all_equal_scores':bool(np.all(scores==scores[0])),'scores_sha256':hashlib.sha256(np.asarray(scores,dtype='<f8').tobytes()).hexdigest(),'error':''}
    except Exception as exc:return {'state_id':state['state_id'],'valid':False,'chosen_index':None,'all_equal_scores':None,'error':type(exc).__name__+': '+str(exc)}

def get_probes(candidate,cache,states,pool_sha,deadline,np,g,t,v,counters):
    check(deadline);key=(candidate['execution_key'],pool_sha)
    start=time.perf_counter();found=[];missing=[]
    for s in states:
        ck=(*key,s['state_id'])
        if ck in cache:found.append(cache[ck]);counters['probe_cache_state_hits']+=1
        else:found.append(None);missing.append((len(found)-1,s,ck))
    if missing:
        fn=None;compile_error=''
        try:fn=v.compile_score(t.program(g.dec(candidate['tree'])))
        except Exception as exc:compile_error=type(exc).__name__+': '+str(exc)
        for index,state,ck in missing:
            check(deadline)
            r=probe_one(np,fn,state) if fn else {'state_id':state['state_id'],'valid':False,'chosen_index':None,'all_equal_scores':None,'error':compile_error}
            cache[ck]=r;found[index]=r;counters['probe_cache_state_misses']+=1
    counters['probe_seconds']+=time.perf_counter()-start
    check(deadline);return found

def choose(seed,attempt,method,meta,variants,parent,models,vocab,states,pool_sha,cache,deadline,np,g,t,v,counters):
    legal=[r for r in variants if r['structure_legal']]
    if not legal:return None
    if not meta['eligible_position_mechanism'] or len(legal)==1:return legal[0]
    counters['rankable_proposals']+=1
    counters['rankable_parent_'+('better' if parent['mean_bins']<2066.4 else 'equal' if parent['mean_bins']==2066.4 else 'worse')]+=1
    uniform=g.choice(legal,g.rng(seed,attempt,10))
    if method=='uniform_position_gp':selected=uniform
    else:
        if method=='behavior_A_position_gp':
            before=get_probes(parent,cache,states,pool_sha,deadline,np,g,t,v,counters)
            for row in legal:
                after=get_probes(row,cache,states,pool_sha,deadline,np,g,t,v,counters)
                paired=[(a,b) for a,b in zip(before,after) if a['valid'] and b['valid']]
                row.update(A_valid=sum(p['valid'] for p in after),A_paired_valid=len(paired),
                    A_all_equal=sum(p['all_equal_scores'] is True for p in after),
                    A_changed=sum(a['chosen_index']!=b['chosen_index'] for a,b in paired),probe_details=after)
        start=time.perf_counter();model=models[method]
        for row in legal:row['rank_score']=rank_score(np,model,row,vocab)
        selected=sorted(legal,key=lambda r:(-r['rank_score'],tie(r)))[0]
        counters['ranking_seconds']+=time.perf_counter()-start
    counters['choice_differs_from_uniform']+=int(selected['trial_index']!=uniform['trial_index'])
    check(deadline);return selected

def fitness_worker(jobfile,outfile):
    start=time.perf_counter();np,g,t,c,prior,v=modules();resource=c.memory_limit();job=load(jobfile)
    result={'valid':False,'mean_bins':None,'instances':[],'error':'','resource_limit':resource,'worker_started_perf':start}
    try:
        candidate=job['candidate'];fn=v.compile_score(t.program(g.dec(candidate['tree'])))
        deadline=job['deadline_perf']
        def bounded(item,bins):check(deadline);return fn(item,bins)
        with warnings.catch_warnings(record=True) as ws:
            warnings.simplefilter('once')
            for inst in c.data('pilot_dev'):
                check(deadline);row,_,_=c.pack(inst,bounded);result['instances'].append({'instance_id':inst['id'],**row})
                save(outfile,{**result,'partial':True})
            result['warnings']=sorted({str(w.message) for w in ws})
        check(deadline);result.update(valid=True,mean_bins=float(np.mean([r['bins_used'] for r in result['instances']])))
    except Exception as exc:result['error']=type(exc).__name__+': '+str(exc)
    result.update(partial=False,worker_finished_perf=time.perf_counter(),worker_wall_seconds=time.perf_counter()-start)
    save(outfile,result)

def evaluate(candidate,folder,token,deadline,counters):
    check(deadline);start=time.perf_counter();job=folder/'jobs'/f'{token}.json';out=folder/'fitness'/f'{token}.json'
    save(job,{'candidate':candidate,'deadline_perf':deadline})
    counters['full_started']+=1
    try:
        proc=subprocess.run([sys.executable,str(Path(__file__).resolve()),'fitness-worker',str(job),str(out)],
            capture_output=True,timeout=max(.001,min(120,deadline-time.perf_counter())),creationflags=subprocess.CREATE_NO_WINDOW)
        errbytes=proc.stderr or b''
        if errbytes:
            log=folder/'worker_stderr'/f'{token}.bin';log.parent.mkdir(exist_ok=True);log.write_bytes(errbytes)
        result=load(out) if out.exists() and proc.returncode==0 else {'valid':False,'mean_bins':None,'instances':[],'error':'WorkerFailure: '+errbytes.decode('utf-8',errors='replace')[-1000:]}
    except subprocess.TimeoutExpired:
        result=load(out) if out.exists() else {'instances':[]}
        result.update(valid=False,mean_bins=None,error='DeadlineTruncated',truncated=True)
    result['evaluation_wall_seconds']=time.perf_counter()-start;counters['full_seconds']+=result['evaluation_wall_seconds']
    if time.perf_counter()>=deadline or result.get('partial'):result.update(valid=False,truncated=True,error='DeadlineTruncated')
    if result.get('truncated'):counters['full_truncated']+=1
    elif result.get('valid'):counters['full_valid']+=1
    else:counters['full_failed']+=1
    return result

def commit(folder,state,deadline):
    check(deadline);seq=state['commits']+1;path=folder/'commits'/f'{seq:06d}.json'
    state['commits']=seq;save(path,state)
    verified=time.perf_counter();check(deadline)
    save(path.with_suffix('.commit'),{'snapshot_sha256':sha(path),'committed_perf':verified})

def run_worker(launchfile):
    launch=load(launchfile);folder=Path(launch['folder']);t0=launch['t0'];deadline=launch['deadline']
    while not (folder/'go.json').exists():
        check(deadline);time.sleep(.002)
    np,g,t,c,prior,v=modules();resource=c.memory_limit();cfg=load(ROOT/'config.json');seed=launch['seed'];method=launch['method']
    state={'seed':seed,'method':method,'t0':t0,'deadline':deadline,'population':[],'best':None,'initial_best':None,'initial_completed':0,
           'attempts_committed':0,'commits':0,'best_events':[],'resource_limit':resource,
           'counters':dict.fromkeys(['proposals_started','trial_sites','over_limit_sites','construction_failures','selected_duplicates','rankable_proposals',
               'eligible_position_proposals','rankable_parent_better','rankable_parent_equal','rankable_parent_worse','choice_differs_from_uniform',
               'probe_cache_state_hits','probe_cache_state_misses','full_started','full_valid','full_failed','full_truncated'],0),
           'parent_reproduction':{},'cost':dict.fromkeys(['probe_seconds','ranking_seconds','full_seconds','proposal_seconds','selection_seconds'],0.)}
    counters=state['counters'];counters.update(state.pop('cost'));cache={};seen=set();models={};vocab=[];states=[]
    try:
        library=g.load_library('raw_fragment_gp')
        # Existing full-root exclusion is enforced by the immutable eligibility index.
        assert sum(map(len,library.values()))==1240
        if method!='uniform_position_gp':
            modelname='frozen_behavior_A_ranker.json' if method=='behavior_A_position_gp' else 'frozen_structure_ranker.json'
            models[method]=load(ROOT/'frozen'/modelname)['model'];vocab=load(ROOT/'frozen/operator_vocabulary.json')
        pool_sha=sha(ROOT/'frozen/states.json')
        if method=='behavior_A_position_gp':
            states=[r for r in load(ROOT/'frozen/states.json') if r['set']=='A'];assert len(states)==64
            for r in states:r['array']=np.asarray(r['feasible_capacities'],dtype=np.float64);r['array'].setflags(write=False)
        planned=load(ROOT/'initialization_plans.json')[str(seed)]
        for slot in range(1,17):
            check(deadline)
            if slot==1:node=t.parse('-(bins - item)')
            else:
                r=g.rng(seed,slot,101);node=t.random_tree('V',r,levels=int(r.integers(1,4)),safe=True)
            p={'id':f'init_{seed}_{slot:02d}',**g.payload(node)}
            assert p['internal_key']==planned[slot-1]['internal_key'] and not g.limits(p)
            result=evaluate(p,folder,f'init_{slot:02d}',deadline,counters);check(deadline)
            child={**p,**result};seen.add(p['execution_key'])
            if child['valid']:
                state['population']=g.selection(state['population']+[child]);state['best']=state['population'][0]
            state['initial_completed']=slot;state['initial_best']=state['best']
            if state['best']:state['best_events'].append({'elapsed':time.perf_counter()-t0,'mean_bins':state['best']['mean_bins'],'id':state['best']['id'],'phase':'init'})
            save(folder/'initialization'/f'{slot:02d}.json',child);commit(folder,state,deadline)
        assert state['population'],'No valid initial candidate'
        attempt=0
        while True:
            check(deadline);attempt+=1;counters['proposals_started']+=1
            start=time.perf_counter();meta,variants,parent=proposal(seed,attempt,state['population'],library,g,t,np)
            counters['proposal_seconds']+=time.perf_counter()-start
            counters['eligible_position_proposals']+=int(meta['eligible_position_mechanism'])
            counters['trial_sites']+=len(variants);counters['over_limit_sites']+=sum(not r['structure_legal'] for r in variants)
            counters['construction_failures']+=int(bool(meta['construction_error']))
            state['parent_reproduction'][parent['execution_key']]=state['parent_reproduction'].get(parent['execution_key'],0)+1
            selected=choose(seed,attempt,method,meta,variants,parent,models,vocab,states,pool_sha,cache,deadline,np,g,t,v,counters)
            event={'attempt':attempt,'seed':seed,'method':method,**meta,'variants':variants,
                'selected_trial':selected['trial_index'] if selected else None,'decision_saved_perf':time.perf_counter(),
                'population_before':[r['id'] for r in state['population']]}
            save(folder/'proposals'/f'{attempt:06d}.json',event);check(deadline)
            if selected:
                p={'id':f'{method}_{seed}_{attempt:06d}',**{k:selected[k] for k in ['tree','expression','execution_key','internal_key','nodes','depth','type']}}
                duplicate=p['execution_key'] in seen;counters['selected_duplicates']+=int(duplicate);seen.add(p['execution_key'])
                result=evaluate(p,folder,f'child_{attempt:06d}',deadline,counters)
                event.update(duplicate=duplicate,evaluation=result);check(deadline)
                child={**p,**result}
                if result['valid']:
                    before=state['best'];start=time.perf_counter();state['population']=g.selection(state['population']+[child]);state['best']=state['population'][0]
                    counters['selection_seconds']+=time.perf_counter()-start
                    event.update(delta_parent=parent['mean_bins']-result['mean_bins'],delta_initial=state['initial_best']['mean_bins']-result['mean_bins'],delta_best=before['mean_bins']-result['mean_bins'])
                    if state['best']['id']!=before['id']:state['best_events'].append({'elapsed':time.perf_counter()-t0,'mean_bins':state['best']['mean_bins'],'id':state['best']['id'],'phase':'search'})
            state['attempts_committed']=attempt;event['completed_elapsed']=time.perf_counter()-t0
            save(folder/'outcomes'/f'{attempt:06d}.json',event);commit(folder,state,deadline)
    except Cutoff:
        save(folder/'cutoff.json',{'at':now(),'elapsed':time.perf_counter()-t0,'reason':'fixed deadline','counters_at_cutoff':counters})

def verify_lock():
    lock=load(ROOT/'execution_lock.json')
    assert sha(ROOT/'registration_lock.json')==lock['registration_lock_sha256']
    for rel,h in lock['files'].items():assert sha(ROOT/rel)==h,rel
    for rel,row in load(ROOT/'source_manifest.json')['workspace_relative_paths'].items():assert sha(BASE/rel)==row['sha256'],rel
    for rel,h in load(ROOT/'registration_lock.json')['files'].items():assert sha(ROOT/rel)==h,rel

def lock_execution():
    assert not (ROOT/'execution_lock.json').exists()
    audit=load(ROOT/'executor_audit.json');assert audit['passed']
    paths=['equal_time.py','process_control.py','check_executor.py','executor_audit.json','execution_environment.json','extension_authorization.json','implementation_change_audit.json']
    save(ROOT/'execution_lock.json',{'at':now(),'registration_lock_sha256':sha(ROOT/'registration_lock.json'),
        'files':{s:sha(ROOT/s) for s in paths},'research_runs_started':0,'models_fitted':0,'new_LLM_calls':0,
        'implementation':'shared proposal, cold per-run probes, selected-only full evaluations, serial120s deadlines and descendant process kill; before research outcomes'})

def finalize(folder,launch,scheduler_result):
    commits=[]
    for marker in sorted((folder/'commits').glob('*.commit')):
        m=load(marker);p=marker.with_suffix('.json')
        assert sha(p)==m['snapshot_sha256']
        if m['committed_perf']<launch['deadline']:commits.append((m,p))
    if commits:
        marker,p=commits[-1];state=load(p);state['last_commit_elapsed']=marker['committed_perf']-launch['t0']
    else:
        state={'initial_completed':0,'best':None,'initial_best':None,'attempts_committed':0,'counters':{},'parent_reproduction':{},'best_events':[],'last_commit_elapsed':None}
    completed=state['attempts_committed'];proposals=list((folder/'proposals').glob('*.json'))
    initial_mean=state['initial_best']['mean_bins'] if state['initial_best'] else None
    best_mean=state['best']['mean_bins'] if state['best'] else None
    fitness_paths=list((folder/'fitness').glob('*.json'))
    physical={'full_jobs_written':len(list((folder/'jobs').glob('*.json'))),'fitness_files':len(fitness_paths),
        'full_valid_results_before_cutoff':0,'partial_or_late_results':0,'instance_records_saved':0}
    for fp in fitness_paths:
        raw=load(fp);physical['instance_records_saved']+=len(raw.get('instances',[]))
        before=raw.get('worker_finished_perf',float('inf'))<launch['deadline']
        physical['full_valid_results_before_cutoff']+=int(raw.get('valid',False) and before and not raw.get('partial'))
        physical['partial_or_late_results']+=int(raw.get('partial',False) or not before)
    result={'seed':launch['seed'],'method':launch['method'],'initial_best_bins':initial_mean,
        'dev_best_bins':best_mean,'dev_gain':initial_mean-best_mean if initial_mean is not None and best_mean is not None else None,
        'initial_completed':state['initial_completed'],'offspring_completed':completed,'proposal_files':len(proposals),
        'last_commit_elapsed':state['last_commit_elapsed'],'counters':state['counters'],'parent_reproduction':state['parent_reproduction'],
        'best_events':state['best_events'],'best':state['best'],'physical':physical,'initialization_complete':state['initial_completed']==16,**scheduler_result}
    save(folder/'complete.json',result)
    final=ROOT/'final_candidates'/f"{launch['method']}_{launch['seed']}"
    save(final.with_suffix('.json'),state['best'])
    np,g,t,c,prior,v=modules()
    final.with_suffix('.py').write_text(t.program(g.dec(state['best']['tree'])) if state['best'] else '# NO VALID CANDIDATE BEFORE DEADLINE\n',encoding='utf-8')
    return result

def search():
    cfg=load(ROOT/'config.json')
    verify_lock();assert not (ROOT/'search_started.json').exists(),'Cannot replay/resume research runs'
    from process_control import Job
    save(ROOT/'search_started.json',{'at':now(),'execution_lock_sha256':sha(ROOT/'execution_lock.json'),'scheduler_pid':os.getpid()})
    with (ROOT/'run_schedule.csv').open(encoding='utf-8-sig',newline='') as f:schedule=list(csv.DictReader(f))
    rows=[];experiment_start=time.perf_counter()
    for row in schedule:
        verify_lock();seed=int(row['search_seed']);method=row['method'];folder=ROOT/'runs'/f'{method}_{seed}'
        folder.mkdir(parents=True,exist_ok=False);(folder/'commits').mkdir()
        job=Job();t0=time.perf_counter();launch={'seed':seed,'method':method,'t0':t0,'deadline':t0+120,'folder':str(folder)}
        save(folder/'launch.json',launch)
        with (folder/'stdout.log').open('w',encoding='utf-8') as out,(folder/'stderr.log').open('w',encoding='utf-8') as err:
            proc=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'run-worker',str(folder/'launch.json')],stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
            job.assign(proc);save(folder/'go.json',{'assigned_pid':proc.pid,'at':now()})
            save(ROOT/'progress.json',{'status':'searching','run_order':int(row['run_order']),'total_runs':cfg['runs'],'method':method,'seed':seed,'started_at':now(),'completed_runs':len(rows),'deadline_perf':launch['deadline']})
            try:proc.wait(timeout=max(.001,launch['deadline']-time.perf_counter()))
            except subprocess.TimeoutExpired:pass
            cutoff=time.perf_counter();running=proc.poll() is None
            if running:job.terminate()
            proc.wait(timeout=10);job.close();finished=time.perf_counter()
        if cutoff<launch['deadline']-.1 and not (folder/'cutoff.json').exists():
            save(ROOT/'infrastructure_failure.json',{'at':now(),'run':row,'returncode':proc.returncode,'stderr':(folder/'stderr.log').read_text(encoding='utf-8',errors='replace')[-3000:]})
            raise RuntimeError('Run stopped before deadline; scheduling halted, no automatic quality-dependent retry')
        result=finalize(folder,launch,{'wall_budget_seconds':120,'scheduler_stop_elapsed':cutoff-t0,'cleanup_seconds':finished-cutoff,
            'deadline_overshoot_seconds':max(0.,cutoff-launch['deadline']),'watchdog_terminated':running,'process_returncode':proc.returncode})
        rows.append(result)
        save(ROOT/'search_summary.json',rows)
        print(json.dumps({'completed_runs':len(rows),'total_runs':cfg['runs'],'method':method,'seed':seed,'offspring_completed':result['offspring_completed']}),flush=True)
    finals={p.relative_to(ROOT).as_posix():sha(p) for p in sorted((ROOT/'final_candidates').glob('*'))}
    assert len(finals)==2*cfg['runs']
    save(ROOT/'outputs_freeze.json',{'at':now(),'files':finals,'completed_runs':cfg['runs'],'execution_lock_sha256':sha(ROOT/'execution_lock.json'),'search_wall_seconds':time.perf_counter()-experiment_start,'new_LLM_calls':0})
    save(ROOT/'progress.json',{'status':'search_completed_outputs_frozen','completed_runs':cfg['runs'],'total_runs':cfg['runs'],'at':now(),'test_data_generated':False})
    print('ALL_SEARCH_RUNS_COMPLETE',flush=True)

if __name__=='__main__':
    command=sys.argv[1]
    if command=='fitness-worker':fitness_worker(sys.argv[2],sys.argv[3])
    elif command=='run-worker':run_worker(sys.argv[2])
    elif command=='lock':lock_execution()
    elif command=='search':search()
    else:raise ValueError(command)
