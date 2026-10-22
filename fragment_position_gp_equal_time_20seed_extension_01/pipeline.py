"""Continue the approved experiment after search; never restarts a GP run."""
import os
for name in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[name]='1'
import hashlib,json,subprocess,sys,time,traceback
from pathlib import Path
import equal_time as x
ROOT=x.ROOT

def main():
    assert not (ROOT/'pipeline_started.json').exists(),'Only one follow-through coordinator is allowed'
    x.save(ROOT/'pipeline_started.json',{'at':x.now(),'pid':os.getpid(),'scope':'wait for all60 outputs,verify reused test data,evaluate,analyze,aggregate30seeds,audit; no GP restart'})
    started=time.time()
    try:
        while not (ROOT/'outputs_freeze.json').exists():
            progress=x.load(ROOT/'progress.json')
            if (ROOT/'infrastructure_failure.json').exists():raise RuntimeError('Search infrastructure failure; no automatic retry')
            if time.time()-(ROOT/'progress.json').stat().st_mtime>300:raise RuntimeError('Search progress stale for>300s; no automatic restart')
            if time.time()-started>9000:raise RuntimeError('Search wait exceeded bounded9000s; inspect existing process, no restart')
            x.save(ROOT/'pipeline_status.json',{'at':x.now(),'status':'waiting_for_search_outputs','completed_runs':progress['completed_runs'],'current_run':progress.get('run_order')})
            time.sleep(10)
        for file,h in x.load(ROOT/'postsearch_code_lock.json')['files'].items():assert x.sha(ROOT/file)==h,file
        for label,args in [('prepare_reused_test',['evaluate_outputs.py','prepare']),('evaluate_frozen_outputs',['evaluate_outputs.py','evaluate']),('analyze',['evaluate_outputs.py','analyze']),('aggregate_original10_plus_new20',['aggregate_30seeds.py']),('final_integrity_audit',['finish_audit.py'])]:
            x.save(ROOT/'pipeline_status.json',{'at':x.now(),'status':label,'completed_runs':60})
            proc=subprocess.run([sys.executable,str(ROOT/args[0]),*args[1:]],capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW)
            log=ROOT/'pipeline_logs'/f'{label}.stdout';log.parent.mkdir(exist_ok=True);log.write_bytes(proc.stdout or b'')
            log.with_suffix('.stderr').write_bytes(proc.stderr or b'')
            if proc.returncode:raise RuntimeError(f'{label} failed, returncode={proc.returncode}; see pipeline_logs, no automatic retries')
        x.save(ROOT/'pipeline_status.json',{'at':x.now(),'status':'complete','completed_runs':60,'audit_passed':x.load(ROOT/'completion_audit.json')['passed'],'report':'REPORT.md'})
        print('EXPERIMENT_COMPLETE',flush=True)
    except Exception as exc:
        x.save(ROOT/'pipeline_failure.json',{'at':x.now(),'error':type(exc).__name__+': '+str(exc),'traceback':traceback.format_exc(),'no_search_restarted':True})
        x.save(ROOT/'pipeline_status.json',{'at':x.now(),'status':'stopped_needs_review','error':str(exc)})
        raise

if __name__=='__main__':main()
