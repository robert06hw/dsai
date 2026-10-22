"""Prepare the user-authorized20 paired-seed extension; no research packing."""
import os
for name in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[name]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
import ast,hashlib,itertools,json,shutil,sys
from pathlib import Path
BASE=Path(__file__).resolve().parent
OLD=BASE/'fragment_position_gp_equal_time_01'
ROOT=BASE/'fragment_position_gp_equal_time_20seed_extension_01'

def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def replace_function(source,name,new):
    node=next(n for n in ast.parse(source).body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name)
    lines=source.splitlines(keepends=True);return ''.join(lines[:node.lineno-1])+new.rstrip()+'\n'+''.join(lines[node.end_lineno:])
def change(source,old,new,count=None):
    found=source.count(old)
    assert found>0 and (count is None or found==count),(old,found,count)
    return source.replace(old,new)

def main():
    assert not ROOT.exists(),'Do not replace or restart an existing extension'
    assert load(OLD/'pipeline_status.json')['status']=='complete' and load(OLD/'completion_audit.json')['passed']
    # Verify all artifacts that define the original methods and sources, and the
    # frozen test bytes. The prior archive itself remains entirely read-only.
    manifest=load(OLD/'manifest.json')['files']
    names=['config.json','equal_time.py','process_control.py','check_executor.py','evaluate_outputs.py','finish_audit.py','pipeline.py',
        'registration_lock.json','execution_lock.json','completion_audit.json','outputs_freeze.json','source_manifest.json','test_data_plan.json',
        'test_data/instances.jsonl','test_data_manifest.csv','test_nonoverlap_audit.json','run_results.csv','test_instance_results.csv','final_summary.json',
        'frozen/frozen_structure_ranker.json','frozen/frozen_behavior_A_ranker.json','frozen/operator_vocabulary.json','frozen/states.json']
    for rel in names:assert sha(OLD/rel)==manifest[rel],rel
    for rel,meta in load(OLD/'source_manifest.json')['workspace_relative_paths'].items():assert sha(BASE/rel)==meta['sha256'],rel
    ROOT.mkdir()
    shutil.copy2(__file__,ROOT/'prepare_extension.py')
    for rel in ['process_control.py','check_executor.py']:
        shutil.copy2(OLD/rel,ROOT/rel)
    shutil.copytree(OLD/'frozen',ROOT/'frozen')
    sys.path.insert(0,str(OLD));import equal_time as old
    np,g,t,c,prior,v=old.modules()
    used=set();seed_sources=[]
    def collect(obj,key=''):
        if isinstance(obj,dict):
            for k,value in obj.items():collect(value,k)
        elif isinstance(obj,list):
            for value in obj:collect(value,key)
        elif 'seed' in key.lower() and isinstance(obj,int):used.add(obj)
    for p in sorted(set(BASE.glob('*/config.json'))|set(BASE.glob('*/test_data_plan.json'))):
        collect(load(p));seed_sources.append({'path':p.relative_to(BASE).as_posix(),'sha256':sha(p)})
    rng=np.random.default_rng(2026101810);seeds=[]
    while len(seeds)<20:
        seed=int(rng.integers(10000000,2000000000))
        if seed not in used and seed not in seeds:seeds.append(seed)
    cfg=load(OLD/'config.json')
    cfg.update(experiment=ROOT.name,version=1,status='extension_registered_not_started',search_seeds=seeds,runs=60,
        nominal_total_search_seconds=7200,user_requested_additional_seeds=20,prior_search_seeds=load(OLD/'config.json')['search_seeds'],
        combined_search_seeds=30,combined_runs=90,prior_cohort=OLD.name,
        test_data='reuse exact original30 B-setting instances; already inspected, no new blind-test claim',
        success_interpretation='fixed-method20-seed replication on already inspected test set; report complete results and intervals; combined30 seeds exploratory after initial10 inspected',
        stop='all60 runs reach120s or objective infrastructure failure; never outcome-dependent refit,threshold,seed extension or automatic restart',
        infrastructure_retry='halt and preserve artifacts on coordinator or I/O infrastructure error; no automatic restart',
        execution_gate='same GP functions and frozen models; only cohort sizes,registration plumbing,reused-data reporting,aggregation changed; verify AST identity before launch')
    save(ROOT/'config.json',cfg)
    save(ROOT/'seed_selection_audit.json',{'salt':2026101810,'RNG':'numpy.default_rng, PCG64, repeated integers[10000000,2000000000), reject recorded seeds and within-cohort duplicates',
        'search_seeds':seeds,'prior_seed_values':sorted(used),'source_configs_and_plans':seed_sources,'no_seed_overlap':not set(seeds)&used,'outcomes_used':False})
    save(ROOT/'extension_authorization.json',{'at':old.now(),'user_request':'這三個方法再分別跑20個seeds','authorized_new_runs':60,'methods':cfg['methods'],'seconds_per_run':120,
        'new_LLM_calls':0,'scope':'20 new paired search seeds, same methods and budget; preserve old10; separately report new20 and combined30; no new test instances'})
    # Exactly the old initialization generator, with20 new RNG seeds.
    initial={}
    for seed in seeds:
        rows=[]
        for slot in range(1,17):
            if slot==1:node=t.parse('-(bins - item)')
            else:
                r=g.rng(seed,slot,101);node=t.random_tree('V',r,levels=int(r.integers(1,4)),safe=True)
            record={'id':f'init_{seed}_{slot:02d}','slot':slot,'source':'Best-fit' if slot==1 else 'basic_random',**g.payload(node)}
            assert not g.limits(record);rows.append(record)
        initial[str(seed)]=rows
    save(ROOT/'initialization_plans.json',initial)
    save(ROOT/'initialization_plan_audit.json',{'seeds':20,'slots_per_seed':16,'planned_slots':320,'physical_initial_slots_at_execution':960,
        'unique_ASTs_per_seed':{s:len({r['execution_key'] for r in rows}) for s,rows in initial.items()},'all_structurally_valid':True,'full_fitness_evaluations':0,'no_history_injected':True})
    permutations=list(itertools.permutations(cfg['methods']))
    orders=permutations*3+[permutations[0],permutations[3]]
    rng.shuffle(orders)
    schedule=[]
    for block,(seed,order) in enumerate(zip(seeds,orders),1):
        for pos,method in enumerate(order,1):schedule.append({'run_order':len(schedule)+1,'seed_block':block,'search_seed':seed,'within_block_order':pos,'method':method,'wall_seconds':120,'status':'planned'})
    import csv
    with (ROOT/'run_schedule.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(schedule[0]));w.writeheader();w.writerows(schedule)
    testplan=load(OLD/'test_data_plan.json')
    testplan.update(status='reuse_locked_original_instances_after_outputs_frozen',new_instances=0,max_programs=63,max_nominal_instance_evaluations=1890,
        reuse_source=f'{OLD.name}/test_data/instances.jsonl',reuse_source_sha256=sha(OLD/'test_data/instances.jsonl'),
        data_generation_gate='do not generate data; after all60 outputs frozen, copy and verify byte-identical original test set',
        content_nonoverlap_audit='original test nonoverlap audit retained; extension intentionally reuses that set',
        previously_inspected=True)
    save(ROOT/'test_data_plan.json',testplan)
    # Copy original runner; only scheduler cohort counters and lock-file lists vary.
    source=(OLD/'equal_time.py').read_text(encoding='utf-8')
    source=change(source,"paths=['equal_time.py','process_control.py','check_executor.py','executor_audit.json','execution_environment.json','execution_amendment_01.json','execution_amendment_02.json']",
        "paths=['equal_time.py','process_control.py','check_executor.py','executor_audit.json','execution_environment.json','extension_authorization.json','implementation_change_audit.json']",1)
    source=change(source,"    verify_lock();assert not (ROOT/'search_started.json').exists()", "    cfg=load(ROOT/'config.json')\n    verify_lock();assert not (ROOT/'search_started.json').exists()",1)
    source=source.replace("'total_runs':30","'total_runs':cfg['runs']").replace("'completed_runs':30","'completed_runs':cfg['runs']")
    source=change(source,'assert len(finals)==60',"assert len(finals)==2*cfg['runs']",1)
    (ROOT/'equal_time.py').write_text(source,encoding='utf-8')
    # Reuse the exact test worker and evaluator. Data preparation now copies the
    # original fixed set, never draws instances or uses test to select programs.
    ev=(OLD/'evaluate_outputs.py').read_text(encoding='utf-8')
    prepare='''def prepare():
    verify_outputs();start=time.perf_counter();assert not (ROOT/'test_inputs_lock.json').exists()
    assert not (ROOT/'test_data').exists(),'Do not replace evaluation data'
    prior=ROOT.parent/'fragment_position_gp_equal_time_01'
    plan=x.load(ROOT/'test_data_plan.json');cfg=x.load(ROOT/'config.json')
    assert x.sha(prior/'test_data/instances.jsonl')==plan['reuse_source_sha256']
    (ROOT/'test_data').mkdir()
    shutil.copy2(prior/'test_data/instances.jsonl',ROOT/'test_data/instances.jsonl')
    for name in ['test_data_manifest.csv','test_nonoverlap_audit.json']:
        shutil.copy2(prior/name,ROOT/name)
    programs=[]
    for seed in cfg['search_seeds']:
        for method in cfg['methods']:
            stem=f'{method}_{seed}';p=ROOT/'final_candidates'/f'{stem}.py';candidate=x.load(p.with_suffix('.json'))
            programs.append({'heuristic':stem,'method':method,'search_seed':seed,'role':'frozen_GP_output','program':p.relative_to(ROOT).as_posix(),'code_sha256':x.sha(p),'valid_output':candidate is not None})
    for name in plan['fixed_references']:
        p=ROOT/'test_rules'/f'{name}.py';p.parent.mkdir(exist_ok=True);shutil.copy2(x.ASSETS/'rules'/f'{name}.py',p)
        programs.append({'heuristic':name,'method':'reference','search_seed':None,'role':'fixed_reference','program':p.relative_to(ROOT).as_posix(),'code_sha256':x.sha(p),'valid_output':True})
    assert len(programs)==cfg['runs']+3
    x.save(ROOT/'test_programs.json',programs)
    x.save(ROOT/'test_data_reuse_audit.json',{'passed':x.sha(ROOT/'test_data/instances.jsonl')==plan['reuse_source_sha256'],'source':plan['reuse_source'],'source_sha256':plan['reuse_source_sha256'],'instances_reused':30,'instances_generated':0,'test_previously_inspected':True,'output_freeze_sha256':x.sha(ROOT/'outputs_freeze.json'),'test_not_used_for_candidate_selection':True})
    paths=['test_data/instances.jsonl','test_data_manifest.csv','test_programs.json','test_nonoverlap_audit.json','test_data_reuse_audit.json','evaluate_outputs.py']+[p['program'] for p in programs]
    x.save(ROOT/'test_inputs_lock.json',{'at':x.now(),'files':{p:x.sha(ROOT/p) for p in paths},'output_freeze_sha256':x.sha(ROOT/'outputs_freeze.json'),'new_searches':0,'new_LLM_calls':0})
    x.save(ROOT/'test_preparation_cost.json',{'wall_seconds':time.perf_counter()-start,'instances_generated':0,'instances_reused':30,'full_evaluations':0})
    print(json.dumps({'test_inputs_locked':True,'reused_instances':30,'programs':len(programs),'new_instances':0}),flush=True)
'''
    ev=replace_function(ev,'prepare',prepare)
    ev=change(ev,"assert lock['completed_runs']==30","assert lock['completed_runs']==x.load(ROOT/'config.json')['runs']",1)
    ev=ev.replace('assert len(allrows)==990',"assert len(allrows)==(x.load(ROOT/'config.json')['runs']+3)*30")
    ev=ev.replace("'nominal_programs':33","'nominal_programs':len(programs)").replace("'nominal_instance_results':990","'nominal_instance_results':len(allrows)")
    ev=change(ev,'assert len(search)==30',"n_seeds=len(cfg['search_seeds'])\n    assert len(search)==cfg['runs']",1)
    ev=change(ev,'assert len(rows)==990',"assert len(rows)==(cfg['runs']+3)*30",1)
    ev=ev.replace("'seeds':10","'seeds':n_seeds").replace('rng.integers(0,10,(10000,10))','rng.integers(0,n_seeds,(10000,n_seeds))').replace('rng.integers(0,10,10)','rng.integers(0,n_seeds,n_seeds)')
    ev=ev.replace('完成 3 方法 × 10 配對種子，每 run 120 秒；新增 LLM 呼叫為 0。搜尋輸出先凍結，之後才生成並評估 30 個新官方 B 設定實例。','完成 3 方法 × {n_seeds} 個新增配對種子，每 run 120 秒；新增 LLM 呼叫為 0。輸出先凍結，之後在原批次已查看的30個B實例評估。這是固定方法的種子重複驗證，沒有生成新測試實例。')
    ev=ev.replace('不把 300 筆 seed×instance 視為獨立重複','不把 600 筆 seed×instance 視為獨立重複').replace('10 種子為有界探索','新增20種子為有界擴充，原10已查看；合併30種子的結果屬探索性').replace('新測試','共用測試')
    ev=ev.replace("'search_runs':30,'search_budget_seconds':3600","'search_runs':cfg['runs'],'search_budget_seconds':cfg['nominal_total_search_seconds']")
    (ROOT/'evaluate_outputs.py').write_text(ev,encoding='utf-8')
    # Adapt cohort counts and provenance only; retain timing and child audits.
    finish=(OLD/'finish_audit.py').read_text(encoding='utf-8')
    finish=finish.replace("assert out['completed_runs']==30","assert out['completed_runs']==cfg['runs']")
    finish=change(finish,"    assert x.load(ROOT/'restart_authorization_02.json')['user_answer']=='同意修正後額外重啟一次'", "    assert cfg['user_requested_additional_seeds']==20",1)
    finish=finish.replace('assert len(summary)==30',"assert len(summary)==cfg['runs']").replace('assert len(init)==10',"assert len(init)==len(cfg['search_seeds'])")
    finish=finish.replace("assert test['nominal_instance_results']==990","assert test['nominal_instance_results']==(cfg['runs']+3)*30")
    oldblock="""    extra=[]
    for name in ['startup_failure_01','startup_failure_02']:
        folder=ROOT/name;manifest=x.load(folder/'archive_manifest.json')
        for rel,h in manifest['files'].items():assert x.sha(folder/rel)==h
        extra.append({'archive':name,'manifest_sha256':x.sha(folder/'archive_manifest.json'),'retained_files':len(manifest['files'])})
"""
    finish=change(finish,oldblock,"    extra=[]\n    assert x.load(ROOT/'test_data_reuse_audit.json')['passed']\n",1)
    finish=finish.replace("'research_runs':30","'research_runs':cfg['runs']").replace("'new_test_instance_results':990","'reused_test_instance_results':test['nominal_instance_results']")
    finish=finish.replace("'approved_extra_startup_retry_recorded':True","'user_requested_20seed_extension':True")
    finish=finish.replace("'nominal_run_seconds':3600","'nominal_run_seconds':cfg['nominal_total_search_seconds']")
    finish=finish.replace("'failed_startups':x.load(ROOT/'execution_amendment_02.json')['archives']","'failed_startups':[]")
    finish=finish.replace("'completed_runs':30","'completed_runs':cfg['runs']").replace("'runs':30,'test_results':990","'runs':cfg['runs'],'test_results':test['nominal_instance_results']")
    start=finish.index("        f.write('\\n## 執行修訂與完整性")
    end=finish.index("        f.write('逐 run",start)
    finish=finish[:start]+"        f.write('\\n## 擴充範圍與完整性\\n\\n本批次為使用者新增20個配對種子的要求，沿用原演算法、凍結模型、120秒上限與同一已查看測試集。原10種子封存不修改，新增20與合併30分開呈現；不將種子擴充解讀為新的盲測。沒有自動補抽或重啟。\\n\\n')\n"+finish[end:]
    (ROOT/'finish_audit.py').write_text(finish,encoding='utf-8')
    pipe=(OLD/'pipeline.py').read_text(encoding='utf-8')
    pipe=pipe.replace('all30','all60').replace("'completed_runs':30","'completed_runs':60").replace('>4500','>9000').replace('bounded4500s','bounded9000s')
    pipe=change(pipe,"('final_integrity_audit',['finish_audit.py'])", "('aggregate_original10_plus_new20',['aggregate_30seeds.py']),('final_integrity_audit',['finish_audit.py'])",1)
    (ROOT/'pipeline.py').write_text(pipe,encoding='utf-8')
    # Hard guard: every online algorithm/evaluator/deadline helper remains AST identical.
    def funcs(src):return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(src).body if isinstance(n,ast.FunctionDef)}
    oldf=funcs((OLD/'equal_time.py').read_text(encoding='utf-8'));newf=funcs(source)
    unchanged=[n for n in oldf if n not in ['search','lock_execution']]
    assert all(oldf[n]==newf[n] for n in unchanged)
    assert funcs((OLD/'evaluate_outputs.py').read_text(encoding='utf-8'))['test_worker']==funcs(ev)['test_worker']
    checks={'passed':True,'unchanged_online_function_ASTs':unchanged,'same_fitness_worker':True,'same_probe_and_position_selector':True,'same_test_worker':True,
        'scheduler_changes_only':['60 run counters,120 file hashes for60 final pairs','extension lock inputs'],'frozen_files_identical':{p.name:sha(p)==sha(OLD/'frozen'/p.name) for p in (ROOT/'frozen').iterdir() if p.is_file()},
        'original_source_manifest_sha256':sha(OLD/'manifest.json'),'original_critical_files_verified':len(names),'research_full_evaluations':0,'new_LLM_calls':0}
    save(ROOT/'implementation_change_audit.json',checks)
    sources=load(OLD/'source_manifest.json')
    for rel in names:
        full=f'{OLD.name}/{rel}';sources['workspace_relative_paths'][full]={'sha256':sha(OLD/rel),'bytes':(OLD/rel).stat().st_size}
    sources['workspace_relative_paths'][f'{OLD.name}/manifest.json']={'sha256':sha(OLD/'manifest.json'),'bytes':(OLD/'manifest.json').stat().st_size}
    save(ROOT/'source_manifest.json',sources)
    (ROOT/'PROTOCOL.md').write_text('''# 等總時間位置排序 GP：新增20配對種子

使用者要求：「這三個方法再分別跑20個seeds」。新增20種子×3方法＝60 runs；每run120秒，名義搜尋上限7200秒。原10種子封存不修改，完成後新增20單獨報告，另合併成每方法30種子共90 runs。

三方法為 uniform_position_gp、structure_position_gp、behavior_A_position_gp。原GP演算法、初始化Best-fit+15基本隨機式、族群上限16、父代選擇與精英保留、算子比例、歷史片段庫、完整程式禁插、結構上限64節點／8深度、凍結排序器、A64探針、快取及120秒截止規則完全沿用。線上函式AST與原執行器逐一核對，見 implementation_change_audit.json。沒有新模型、回訓、門檻或LLM呼叫。

每個新種子三方法共用同一初始化計畫，各自在自己的120秒內重新生成、評估；全部初始化、試插、探針、推論、完整評估、失敗、重複、選拔與線上檔案寫入皆計時。一次只能跑一個run與一個候選worker，BLAS單執行緒。晚完成或未提交結果不算收益。種子及平衡隨機順序事前固定，不按中途勝負換種子或增加時間。基礎設施問題停止並留存，不自動重啟。

搜尋只用原pilot_dev。全部60個輸出依開發最佳凍結後，在原10種子使用的同一30個官方B設定實例上評估。原測試檔雜湊固定，容量100、每例5000物品，沿用原物品順序、評分與平手介面。新增測試實例為0。這批測試已查看過，因此擴充是固定方法的搜尋種子重複驗證。

主要終點仍是各種子30例平均後的「結構排序箱數−行為A箱數」，正值表示A較好；報新增20種子全部結果及配對種子bootstrap10000次95%區間，並報跨種子與實例區間、隨機位置對照、有效率、成本、學習／排序機會與品質時間曲線。不把600筆seed×instance當獨立樣本。原10已查看，新增20與合併30分開報告。

合併表包含90筆run摘要與2790筆逐例結果（90個輸出×30例＋3個固定參考×30例）；固定參考只列一次，並核對兩批參考箱數與決策雜湊。原10與新增20的差異分層報告。20種子擴充全部陰性或失敗結果亦保留，不按正例補抽。

啟動前先跑手寫樹、合成狀態、實際鎖檔與程序樹終止稽核，再鎖定來源、設定、種子、共同初始化、排程、執行器及後續分析程式。搜尋輸出鎖定後才執行共用測試。完整軌跡與成本另存本目錄，不修改原封存、不上傳GitHub。
''',encoding='utf-8')
    save(ROOT/'preparation_state.json',{'at':old.now(),'status':'plans_and_adapted_runner_prepared','seed_count':20,'runs':60,'search_budget_seconds':7200,'prior_runs_preserved':30,'research_full_evaluations':0,'new_LLM_calls':0,
        'next':'add fixed aggregation code,run prelaunch checks,and freeze registration/execution/postsearch locks before search'})
    print(json.dumps({'prepared':str(ROOT),'seeds':seeds,'runs':60,'seconds':7200,'online_functions_identical':True,'new_LLM_calls':0}))

if __name__=='__main__':main()
