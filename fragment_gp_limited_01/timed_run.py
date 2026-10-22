"""Observe wall clocks and timestamps without changing locked search choices."""
import json, platform, sys, threading, time
from pathlib import Path
import gp_search as g
import cpu as c
import numpy as np
ROOT=g.ROOT
original_save=g.save
original_evaluate=g.evaluate
original_run=g.run_one
clock_local=threading.local()

def measured_save(path,obj):
    if Path(path).name=='checkpoint.json' and hasattr(clock_local,'start'):
        elapsed=clock_local.previous+time.perf_counter()-clock_local.start
        obj['cumulative_run_seconds']=elapsed
        if obj['log']:obj['log'][-1]['cumulative_run_seconds']=elapsed
    return original_save(path,obj)

def measured_evaluate(p,split='pilot_dev'):
    out=ROOT/'evaluations'/f"{split}_{p['id']}.json";was_saved=out.exists();start=c.now()
    result=original_evaluate(p,split)
    if not was_saved:
        result['evaluation_started_at']=start;result['evaluation_completed_at']=c.now()
        original_save(out,result)
    return result

def measured_run(seed,method):
    checkpoint=ROOT/'runs'/f'{method}_{seed}'/'checkpoint.json'
    clock_local.previous=c.load(checkpoint).get('cumulative_run_seconds',0) if checkpoint.exists() else 0
    clock_local.start=time.perf_counter()
    completed=ROOT/'runs'/f'{method}_{seed}'/'complete.json';already=completed.exists()
    row=original_run(seed,method)
    if not already:
        row['actual_run_cumulative_seconds']=clock_local.previous+time.perf_counter()-clock_local.start
        row['timing_scope']='full run, includes construction, selection, candidate evaluation, checkpoint I/O; shared initialization separately counted'
        original_save(completed,row)
    return row

if __name__=='__main__':
    g.check_lock();lock=ROOT/'execution_instrumentation_lock.json'
    if not lock.exists():
        assert not list((ROOT/'evaluations').glob('*.json')),'Instrumentation must be locked before first candidate evaluation'
        original_save(lock,{'locked_at':c.now(),'search_settings_unchanged':True,
            'files':{name:c.sha((ROOT/name).read_bytes()) for name in ['timed_run.py','RUN_SEARCH.md','pre_search_lock.json']}})
    for rel,h in c.load(lock)['files'].items():assert c.sha((ROOT/rel).read_bytes())==h,rel
    g.save=measured_save;g.evaluate=measured_evaluate;g.run_one=measured_run
    start=time.perf_counter();g.run()
    original_save(ROOT/'runtime_environment.json',{'python':sys.version,'numpy':np.__version__,'platform':platform.platform(),
        'executable':sys.executable,'completed_at':c.now(),'invocation_including_instrumentation_wall_seconds':time.perf_counter()-start,
        'timing_note':'No interruption expected; cumulative clocks exclude any future uncheckpointed interrupted fragments.'})
