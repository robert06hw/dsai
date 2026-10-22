"""Freeze a bounded GP experiment plan. No packing, model fit, or GP runs."""
import os
for env_name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[env_name]='1'
import collections,csv,hashlib,json,platform,random,shutil,sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import numpy as np

ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent
METHODS=['uniform_position_gp','structure_position_gp','behavior_A_position_gp']
SALT=2026101807

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')

def main():
    assert not (ROOT/'registration_lock.json').exists(),'Registration is immutable; use audit_registration.py.'
    sys.path.insert(0,str(BASE/'fragment_gp_limited_01'))
    import gp_search as g
    import typed_tree as t
    rng=random.Random(SALT)
    # Exclude seed values in the existing cohort configs before choosing new plans.
    prior_seeds=set()
    def collect(value,key=''):
        if isinstance(value,dict):
            for k,v in value.items():collect(v,k)
        elif isinstance(value,list):
            for v in value:collect(v,key)
        elif 'seed' in key.lower() and isinstance(value,int):prior_seeds.add(value)
    seed_sources=[]
    for p in sorted(BASE.glob('*/config.json')):
        if p.parent==ROOT:continue
        collect(load(p));seed_sources.append({'path':p.relative_to(BASE).as_posix(),'sha256':sha(p)})
    pool=[s for s in rng.sample(range(10000000,100000000),100) if s not in prior_seeds]
    seeds=pool[:10];test_seeds=pool[10:40];backup_seeds=pool[40:70]
    assert len(set(seeds+test_seeds+backup_seeds))==70
    save(ROOT/'seed_selection_audit.json',{'sampling':'Python random.Random(2026101807).sample(range(10000000,100000000),100); exclude seed fields of listed configs; first10 search,next30 test,next30 backups',
        'source_configs':seed_sources,'previous_seed_values':sorted(prior_seeds),'no_seed_overlap':not set(seeds+test_seeds+backup_seeds)&prior_seeds,
        'content_overlap_check':'pending until new data generation; seed novelty does not establish item novelty'})
    config={
        'experiment':'fragment_position_gp_equal_time_01','version':1,'status':'preregistered_only_not_executed',
        'methods':METHODS,'primary_method':'behavior_A_position_gp','primary_control':'structure_position_gp',
        'search_seeds':seeds,'runs':30,'wall_seconds_per_run':120,'nominal_total_search_seconds':3600,
        'selection_budget':'time only; no fixed128-candidate cap','population_max':16,'initial_slots':16,
        'initialization':'Best-fit +15 typed basic random expressions; same plans per paired seed; generated/evaluated afresh within each run clock; duplicates not replenished',
        'operator_block':{'length':112,'crossover':56,'subtree_replace':39,'constant_mutation':17,
            'rng':'numpy.default_rng(SeedSequence([seed,block_index,102])); block_index starts0; shuffle original concatenated quota list; prefix if cutoff'},
        'fragment_probability_within_subtree_replacement':0.5,'max_emitted_nodes':64,'max_emitted_depth':8,
        'parent_selection':'uniform current retained population; with replacement','survival':'mean bins,nodes,execution key; unique execution AST; max16',
        'new_position_mechanism':{'scope':'historical fragment replacement with non-root V anchor only','trial_sites_max':3,
            'sites':'original uniform anchor plus up to2 uniform without-replacement other internal V paths; canonical path sort before sampling',
            'additional_sites_rng_channel':9,'uniform_legal_choice_rng_channel':10,'zero_legal':'paid failed proposal, no redraw',
            'one_legal':'direct full evaluation without unnecessary ranking probes','multiple_legal':'select one; save choices before full evaluation',
            'other_operations':'unchanged original single-site proposal','parent_quality_gate':None},
        'ranker':'frozen structure and behavior_A, vocabulary, scaling, salt2026101803 unchanged; no fit or threshold',
        'online_states':'A64 only; B64 not executed','probe_cache':'per-run execution AST + state pool SHA + state_id; cache valid/failure outputs; charge lookup/miss; cold per run',
        'full_fitness_cache':False,'duplicate_policy':'consume proposal and full-evaluate valid selected duplicate; no refill',
        'timer':'scheduler perf_counter before launching fresh process; deadline=t0+120s; all online preparation and initialization charged',
        'deadline_policy':'terminate work; only complete five-instance fitness committed before deadline enters population; no late promotion; cleanup separately reported',
        'workers_simultaneous_runs':1,'workers_candidate_per_run':1,'blas_threads':1,'memory_bytes_each':536870912,
        'candidate_timeout_seconds':'min(120,run remaining seconds)','resume':False,
        'search_data':'frozen pilot_dev, five5000-item instances,capacity100,pilot floor rounding',
        'test_data':'30 unseen official-setting round instances, generate only after all outputs hash-frozen',
        'primary_delta':'mean across paired search seeds of mean(test bins_structure - test bins_behavior_A) across all30 instances',
        'primary_CI':'paired search-seed percentile bootstrap10000; conditional on test instances',
        'secondary_CI':'crossed independent search-seed x instance bootstrap10000',
        'bootstrap_seed':2026101808,'anytime_seconds':[30,60,90,120],
        'success_interpretation':'positive main difference with supporting95% interval, consistent secondary contrast vs uniform, no validity/cost violation; otherwise report uncertainty; exploratory10 seeds',
        'infrastructure_retry':'at most one whole three-method seed block restart for objective infrastructure fault before inspecting its quality; retain all failed artifacts; never retry for invalid or poor candidates',
        'stop':'all30 runs reach120s or objective failure; no outcome-dependent extension, refit, threshold, seed additions',
        'new_LLM_requests':0,'executed_search_runs':0,'executed_full_evaluations':0,
        'execution_gate':'new runner implementation and deadline audit still required and hash-locked before any research run; this directory registers design only'
    }
    save(ROOT/'config.json',config)
    # Balanced block order: all six permutations once, remaining four chosen
    # before outcomes; each method has3/3/4 occurrences in each order position.
    import itertools
    permutations=list(itertools.permutations(METHODS));rng.shuffle(permutations)
    extras=[(METHODS[0],METHODS[1],METHODS[2]),(METHODS[1],METHODS[2],METHODS[0]),
            (METHODS[2],METHODS[0],METHODS[1]),(METHODS[0],METHODS[2],METHODS[1])]
    orders=permutations+extras;rng.shuffle(orders)
    schedule=[]
    for block,(seed,order) in enumerate(zip(seeds,orders),1):
        for pos,method in enumerate(order,1):schedule.append({'run_order':len(schedule)+1,'seed_block':block,'search_seed':seed,'within_block_order':pos,'method':method,'wall_seconds':120,'status':'planned'})
    with (ROOT/'run_schedule.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(schedule[0]));w.writeheader();w.writerows(schedule)
    initial={}
    for seed in seeds:
        rows=[]
        for slot in range(1,17):
            if slot==1:node=t.parse('-(bins - item)')
            else:
                r=g.rng(seed,slot,101);node=t.random_tree('V',r,levels=int(r.integers(1,4)),safe=True)
            p={'id':f'init_{seed}_{slot:02d}','slot':slot,'source':'Best-fit' if slot==1 else 'basic_random',**g.payload(node)}
            assert not g.limits(p);rows.append(p)
        initial[str(seed)]=rows
    save(ROOT/'initialization_plans.json',initial)
    save(ROOT/'initialization_plan_audit.json',{'seeds':len(initial),'slots_per_seed':16,'planned_slots':160,
        'physical_initial_slots_at_execution':480,'unique_execution_ASTs_per_seed':{s:len({r['execution_key'] for r in rows}) for s,rows in initial.items()},
        'all_structurally_valid':True,'fitness_evaluations':0,'historical_full_program_injections':0,'duplicates_retained_not_refilled':True})
    save(ROOT/'test_data_plan.json',{'status':'not_generated_not_evaluated','instances':30,'seeds':test_seeds,'duplicate_only_backup_seeds':backup_seeds,
        'RNG':'numpy.random.default_rng(seed), PCG64, one independent generator per instance',
        'shape':3,'scale':45,'clip':[1,100],'rounding':'np.round ties-to-even','capacity':100,'items_per_instance':5000,
        'repository_commit':'472545785c936dcfc863d2bc0d6109cf23c7ce62',
        'official_generator_sha256':'02556b60c67e769aa8f012783244eb81861f8a1d59f0e90756466ab8c6315c52',
        'data_generation_gate':'all30 final outputs frozen first; verify official generator bytes; archive all existing project data sources before content-hash audit',
        'content_nonoverlap_audit':'pending, required at generation; no quality-informed data replacement',
        'max_programs':33,'max_nominal_instance_evaluations':990,'fixed_references':['Best-fit','EoH','Historical-best']})
    src=BASE/'fragment_position_ranking_explore_01'
    for name in ['frozen_structure_ranker.json','frozen_behavior_A_ranker.json','operator_vocabulary.json']:
        target=ROOT/'frozen'/name;target.parent.mkdir(exist_ok=True);shutil.copy2(src/name,target)
    shutil.copy2(BASE/'fragment_position_diagnostic_01/states.json',ROOT/'frozen/states.json')
    expected=load(src/'frozen_candidates_lock.json')
    # File hash map varies only in the envelope, not expected values.
    assert sha(ROOT/'frozen/frozen_structure_ranker.json')=='d9632eb3effe460ba682812db2ea231e9bd6961d94840eb5b071c1c67f1d6146'
    assert sha(ROOT/'frozen/frozen_behavior_A_ranker.json')=='b7e476c8c796bf0c9a2136ae3b60b223de45f2638c75bb8e211ce8e2e73e33fa'
    relative_sources=[
        'fragment_gp_limited_01/gp_search.py','fragment_gp_limited_01/config.json','fragment_gp_limited_01/cpu.py',
        'fragment_gp_limited_01/typed_tree.py','fragment_gp_limited_01/historical_prior.py',
        'fragment_gp_limited_01/historical_validator.py','fragment_gp_limited_01/historical_purity.py','fragment_gp_limited_01/scoring.py',
        'fragment_gp_limited_01/libraries/raw_fragments.json','fragment_gp_limited_01/sources/historical_tree_index.json',
        'dsai/assets/data/pilot_dev.jsonl','dsai/assets/data/pilot_val.jsonl','dsai/assets/data/test_B.jsonl',
        'dsai/assets/rules/Best-fit.py','dsai/assets/rules/EoH.py','dsai/assets/rules/Historical-best.py',
        'fragment_gp_limited_test_01/validate.py','fragment_gp_limited_test_01/config.json',
        'fragment_position_ranking_explore_01/explore.py','fragment_position_ranking_explore_01/frozen_candidates_lock.json',
        'fragment_position_ranking_explore_01/frozen_structure_ranker.json','fragment_position_ranking_explore_01/frozen_behavior_A_ranker.json',
        'fragment_position_ranking_explore_01/operator_vocabulary.json','fragment_position_diagnostic_01/states.json',
        'fragment_position_ranking_validation_01/summary.json','fragment_position_ranking_validation_01/completion_audit.json']
    save(ROOT/'source_manifest.json',{'workspace_relative_paths':{s:{'sha256':sha(BASE/s),'bytes':(BASE/s).stat().st_size} for s in relative_sources},'old_archives_modified':False})
    save(ROOT/'registration_environment.json',{'at':datetime.now(ZoneInfo('Asia/Taipei')).isoformat(),'python':sys.version,'executable':sys.executable,
        'numpy':np.__version__,'OS':platform.platform(),'machine':platform.machine(),'processor':platform.processor(),'logical_cpus':os.cpu_count(),
        'note':'registration environment only; execution must record actual CPU model,affinity,OS,versions and worker counts at launch'})
    save(ROOT/'registration_lock.json',{'locked_at':datetime.now(ZoneInfo('Asia/Taipei')).isoformat(),'stage':'design_registered_search_not_started',
        'files':{p.relative_to(ROOT).as_posix():sha(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name not in ['registration_lock.json','registration_audit.json']},
        'new_search_runs':0,'new_full_packing_evaluations':0,'new_LLM_requests':0,'test_instances_generated':0})
    print(json.dumps({'status':'registered_not_executed','runs':30,'seconds_per_run':120,'total_search_upper_seconds':3600,'search_seeds':seeds,'initialization_plans':160,'full_evaluations':0}))

if __name__=='__main__':main()
