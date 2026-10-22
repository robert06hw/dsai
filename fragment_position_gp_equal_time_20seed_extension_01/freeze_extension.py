"""Final static/statistical plan checks and immutable locks, no GP fitness."""
import os
for name in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[name]='1'
import ast,collections,csv,json
from pathlib import Path
import equal_time as x
ROOT=x.ROOT

def main():
    assert not (ROOT/'registration_lock.json').exists() and not (ROOT/'execution_lock.json').exists()
    cfg=x.load(ROOT/'config.json');np,g,t,c,prior,v=x.modules()
    assert len(cfg['search_seeds'])==len(set(cfg['search_seeds']))==20
    assert not set(cfg['search_seeds'])&set(cfg['prior_search_seeds'])
    assert cfg['runs']==60 and cfg['wall_seconds_per_run']==120 and cfg['nominal_total_search_seconds']==7200
    with (ROOT/'run_schedule.csv').open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
    assert len(rows)==60 and sum(int(r['wall_seconds']) for r in rows)==7200
    assert [int(r['run_order']) for r in rows]==list(range(1,61))
    counts={}
    for m in cfg['methods']:
        rs=[r for r in rows if r['method']==m];assert len(rs)==20 and {int(r['search_seed']) for r in rs}==set(cfg['search_seeds'])
        counts[m]=dict(collections.Counter(int(r['within_block_order']) for r in rs));assert max(counts[m].values())-min(counts[m].values())<=1
    plans=x.load(ROOT/'initialization_plans.json');assert set(plans)==set(map(str,cfg['search_seeds']))
    for seed,rs in plans.items():
        assert len(rs)==16 and rs[0]['source']=='Best-fit'
        for row in rs:assert not g.limits(g.payload(g.dec(row['tree'])))
    # Exact original ASTs for every online component, including serialization,
    # initialization/evaluation, deadline commits, selection and finalization.
    def functions(p):return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(p.read_text(encoding='utf-8')).body if isinstance(n,ast.FunctionDef)}
    old=ROOT.parent/'fragment_position_gp_equal_time_01';before=functions(old/'equal_time.py');after=functions(ROOT/'equal_time.py')
    same=[n for n in before if n not in ['search','lock_execution']]
    assert all(before[n]==after[n] for n in same)
    assert functions(old/'evaluate_outputs.py')['test_worker']==functions(ROOT/'evaluate_outputs.py')['test_worker']
    for p in ROOT.glob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
    from aggregate_30seeds import compare
    arrays={'behavior_A_position_gp':np.ones((20,30)),'structure_position_gp':np.full((20,30),2.),'uniform_position_gp':np.full((20,30),3.)}
    test=compare(np,arrays,list(range(20)),2026101812)
    assert test[0]['delta_control_minus_focal']==1 and test[0]['paired_seed_CI95']==[1.,1.] and test[0]['crossed_seed_instance_CI95']==[1.,1.] and test[0]['seed_wins']==20
    zeros=compare(np,{m:np.zeros((20,30)) for m in cfg['methods']},list(range(20)),2026101812)
    assert all(r['paired_seed_CI95']==[0.,0.] and r['seed_ties']==20 for r in zeros)
    assert x.load(ROOT/'executor_audit.json')['passed']
    for rel,meta in x.load(ROOT/'source_manifest.json')['workspace_relative_paths'].items():assert x.sha(ROOT.parent/rel)==meta['sha256'],rel
    for name in ['registration_audit.json','registration_lock.json','execution_lock.json','postsearch_code_lock.json','search_started.json','outputs_freeze.json']:
        assert not (ROOT/name).exists()
    audit={'at':x.now(),'passed':True,'paired_seeds':20,'runs':60,'seconds_per_run':120,'total_nominal_seconds':7200,
        'all_online_function_ASTs_identical':same,'randomized_balanced_order':counts,'initialization_plans':320,
        'full_fitness_evaluations':0,'new_LLM_calls':0,'new_test_instances':0,'reused_test_previously_inspected':True,
        'generic_bootstrap20_seed_fixture_passed':True,'sources_unchanged':True,'original10_preserved':True,'source_output_already_inspected':True}
    x.save(ROOT/'registration_audit.json',audit)
    # Registration includes code and prelaunch audit; subsequent statuses are
    # separate historical records, so frozen files are never rewritten.
    files={p.relative_to(ROOT).as_posix():x.sha(p) for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and 'executor_checks' not in p.parts and not p.name.endswith('.tmp')}
    x.save(ROOT/'registration_lock.json',{'at':x.now(),'stage':'new20_seeds_locked_before_search','files':files,'research_runs_started':0,'new_LLM_calls':0})
    post=['evaluate_outputs.py','aggregate_30seeds.py','finish_audit.py','pipeline.py']
    x.save(ROOT/'postsearch_code_lock.json',{'at':x.now(),'files':{p:x.sha(ROOT/p) for p in post},'test_data_policy':'reuse exact original30,already inspected; no generation; fixed dev-best selection','aggregate_policy':'original10+new20,90runs2790rows,3refs once,exploratory'})
    x.lock_execution();x.verify_lock()
    print(json.dumps({'locked':True,'runs':60,'paired_seeds':20,'search_seconds':7200,'original_online_functions_identical':True,'new_test_instances':0,'new_LLM_calls':0}))

if __name__=='__main__':main()
