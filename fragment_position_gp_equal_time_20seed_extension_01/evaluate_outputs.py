"""After all GP outputs are frozen: new data, fixed-output test, analysis.

This file never imports the GP run entry point as a command, calls a model fit,
or selects candidates by test quality. No search or LLM request is made here.
"""
import os
for name in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[name]='1'
import collections,csv,importlib.util,json,shutil,subprocess,sys,time,warnings
from pathlib import Path
import equal_time as x
ROOT=x.ROOT

def table(path,rows):
    rows=list(rows);path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        fields=list(dict.fromkeys(k for r in rows for k in r))
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows({k:json.dumps(v) if isinstance(v,(list,dict)) else v for k,v in r.items()} for r in rows)
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def verify_outputs():
    x.verify_lock();lock=x.load(ROOT/'outputs_freeze.json');assert lock['completed_runs']==x.load(ROOT/'config.json')['runs']
    for rel,h in lock['files'].items():assert x.sha(ROOT/rel)==h,rel
    return lock

def prepare():
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

def test_worker(jobfile,outfile):
    np,g,t,c,prior,v=x.modules();resource=c.memory_limit();job=x.load(jobfile);rec=job['program'];rows=[]
    if rec['role']=='fixed_reference':
        ns={'np':np};exec(compile((ROOT/rec['program']).read_text(encoding='utf-8'),rec['heuristic'],'exec'),ns);fn=ns['score']
    elif rec['valid_output']:fn=v.compile_score((ROOT/rec['program']).read_text(encoding='utf-8'))
    else:fn=None
    for inst in [json.loads(s) for s in (ROOT/'test_data/instances.jsonl').read_text(encoding='utf-8').splitlines()]:
        start=time.perf_counter();deadline=start+120
        def bounded(item,bins):
            x.check(deadline)
            if fn is None:raise ValueError('No valid candidate before search deadline')
            return fn(item,bins)
        try:
            with warnings.catch_warnings(record=True) as ws:
                warnings.simplefilter('once');r,_,_=c.pack(inst,bounded)
            row={'dataset':'new_B_equal_time','instance_id':inst['id'],'bins_used':r['bins_used'],'runtime':r['runtime'],'cpu_seconds':r['cpu_seconds'],'trace_hash':r['trace_hash'],'chosen_capacity_hash':r['chosen_capacity_hash'],'valid':True,'error':'','warnings':sorted({str(w.message) for w in ws})}
        except Exception as exc:row={'dataset':'new_B_equal_time','instance_id':inst['id'],'bins_used':None,'runtime':time.perf_counter()-start,'valid':False,'error':type(exc).__name__+': '+str(exc)}
        rows.append(row);x.save(outfile,{'program':rec['program'],'code_sha256':rec['code_sha256'],'resource_limit':resource,'instances':rows,'complete':len(rows)==30})

def evaluate():
    verify_outputs();start=time.perf_counter();lock=x.load(ROOT/'test_inputs_lock.json')
    for p,h in lock['files'].items():assert x.sha(ROOT/p)==h,p
    assert not (ROOT/'test_complete.json').exists()
    programs=x.load(ROOT/'test_programs.json');groups=collections.defaultdict(list)
    for p in programs:groups[p['code_sha256']].append(p)
    allrows=[]
    for index,(h,ps) in enumerate(groups.items(),1):
        job=ROOT/'test_jobs'/f'{h}.json';out=ROOT/'test_evaluations'/f'{h}.json'
        assert not out.exists(),'Do not silently rerun test outcomes'
        x.save(job,{'program':ps[0]})
        proc=subprocess.run([sys.executable,str(Path(__file__).resolve()),'worker',str(job),str(out)],capture_output=True,timeout=3630,creationflags=subprocess.CREATE_NO_WINDOW)
        if proc.returncode!=0 or not out.exists():raise RuntimeError('Test worker infrastructure failure: '+(proc.stderr or b'').decode('utf-8',errors='replace')[-2000:])
        result=x.load(out);assert result['complete'] and len(result['instances'])==30
        for p in ps:
            for row in result['instances']:allrows.append({'heuristic':p['heuristic'],'method':p['method'],'search_seed':p['search_seed'],'role':p['role'],'code_sha256':h,**row})
        table(ROOT/'test_instance_results.csv',allrows)
        x.save(ROOT/'test_progress.json',{'at':x.now(),'unique_programs_done':index,'unique_programs':len(groups),'nominal_rows_saved':len(allrows)})
        print(json.dumps({'test_programs_complete':index,'unique_programs':len(groups)}),flush=True)
    assert len(allrows)==(x.load(ROOT/'config.json')['runs']+3)*30
    x.save(ROOT/'test_complete.json',{'at':x.now(),'wall_seconds':time.perf_counter()-start,'nominal_programs':len(programs),'physical_unique_programs':len(groups),'nominal_instance_results':len(allrows),'physical_instance_evaluations':len(groups)*30,'results_sha256':x.sha(ROOT/'test_instance_results.csv'),'new_searches':0,'new_LLM_calls':0})

def analyze():
    verify_outputs();np,g,t,c,prior,v=x.modules();cfg=x.load(ROOT/'config.json');search=x.load(ROOT/'search_summary.json')
    n_seeds=len(cfg['search_seeds'])
    assert len(search)==cfg['runs']
    with (ROOT/'test_instance_results.csv').open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
    assert len(rows)==(cfg['runs']+3)*30
    ids=sorted({r['instance_id'] for r in rows});assert len(ids)==30
    test_by={}
    for method in cfg['methods']:
        matrix=[]
        for seed in cfg['search_seeds']:
            rs={r['instance_id']:r for r in rows if r['method']==method and int(r['search_seed'])==seed}
            assert set(rs)==set(ids)
            matrix.append([float(rs[i]['bins_used']) if rs[i]['valid']=='True' else float('nan') for i in ids])
        test_by[method]=np.asarray(matrix)
    summary=[];perseed=[]
    for method in cfg['methods']:
        rs=[r for r in search if r['method']==method];a=test_by[method]
        summary.append({'method':method,'seeds':n_seeds,'test_valid_results':int(np.isfinite(a).sum()),'test_mean_bins':float(a.mean()) if np.all(np.isfinite(a)) else None,
            'test_seed_mean_std':float(a.mean(axis=1).std(ddof=1)) if np.all(np.isfinite(a)) else None,
            'dev_mean_bins':float(np.mean([r['dev_best_bins'] for r in rs])) if all(r['dev_best_bins'] is not None for r in rs) else None,
            'mean_dev_gain':float(np.mean([r['dev_gain'] for r in rs])) if all(r['dev_gain'] is not None for r in rs) else None,
            'offspring_completed':sum(r['offspring_completed'] for r in rs),'mean_offspring_completed':float(np.mean([r['offspring_completed'] for r in rs])),
            'rankable_proposals':sum(r['counters'].get('rankable_proposals',0) for r in rs),
            'probe_seconds_committed':sum(r['counters'].get('probe_seconds',0) for r in rs),'ranking_seconds_committed':sum(r['counters'].get('ranking_seconds',0) for r in rs),
            'full_jobs_written':sum(r['physical']['full_jobs_written'] for r in rs),'total_scheduler_stop_seconds':sum(r['scheduler_stop_elapsed'] for r in rs)})
        for k,seed in enumerate(cfg['search_seeds']):
            s=next(r for r in rs if r['seed']==seed)
            perseed.append({'seed':seed,'method':method,'dev_initial':s['initial_best_bins'],'dev_final':s['dev_best_bins'],'dev_gain':s['dev_gain'],
                'test_mean_bins':float(a[k].mean()) if np.all(np.isfinite(a[k])) else None,'offspring_completed':s['offspring_completed'],
                'rankable_proposals':s['counters'].get('rankable_proposals',0),'scheduler_stop_seconds':s['scheduler_stop_elapsed']})
    comparisons=[]
    for focal,control in [('behavior_A_position_gp','structure_position_gp'),('behavior_A_position_gp','uniform_position_gp'),('structure_position_gp','uniform_position_gp')]:
        d=test_by[control]-test_by[focal];valid=bool(np.all(np.isfinite(d)))
        r={'focal':focal,'control':control,'primary':focal=='behavior_A_position_gp' and control=='structure_position_gp','complete_all_pairs':valid}
        if valid:
            rng=np.random.default_rng(cfg['bootstrap_seed']);di=d.mean(axis=1)
            bs=np.mean(di[rng.integers(0,n_seeds,(10000,n_seeds))],axis=1)
            crossed=[]
            for k in range(10000):crossed.append(float(d[np.ix_(rng.integers(0,n_seeds,n_seeds),rng.integers(0,30,30))].mean()))
            r.update(delta_control_minus_focal=float(d.mean()),paired_seed_CI95=np.quantile(bs,[.025,.975]).tolist(),crossed_seed_instance_CI95=np.quantile(crossed,[.025,.975]).tolist(),
                median_seed_delta=float(np.median(di)),seed_wins=int((di>0).sum()),seed_ties=int((di==0).sum()),seed_losses=int((di<0).sum()),per_seed_delta=di.tolist())
        else:r['conclusion']='test failures prevent a complete primary paired claim; do not drop seeds'
        comparisons.append(r)
    table(ROOT/'run_results.csv',perseed);table(ROOT/'method_summary.csv',summary);x.save(ROOT/'comparisons.json',comparisons)
    refs=[]
    for name in ['Best-fit','EoH','Historical-best']:
        rs=[r for r in rows if r['heuristic']==name];assert len(rs)==30
        refs.append({'heuristic':name,'mean_bins':float(np.mean([float(r['bins_used']) for r in rs])) if all(r['valid']=='True' for r in rs) else None,'valid_instances':sum(r['valid']=='True' for r in rs)})
    table(ROOT/'reference_summary.csv',refs)
    anytime=[];parents=[];cost=[]
    for s in search:
        for second in cfg['anytime_seconds']:
            eligible=[r for r in s['best_events'] if r['elapsed']<=second]
            anytime.append({'seed':s['seed'],'method':s['method'],'elapsed_seconds':second,'best_mean_bins':min(r['mean_bins'] for r in eligible) if eligible else None})
        for parent,count in s['parent_reproduction'].items():parents.append({'seed':s['seed'],'method':s['method'],'parent_execution_AST':parent,'reproductions':count})
        positive=[e for e in s['best_events'] if e['phase']=='search' and s['initial_best_bins'] is not None and e['mean_bins']<s['initial_best_bins']]
        final=[e for e in s['best_events'] if e['mean_bins']==s['dev_best_bins']]
        cost.append({'seed':s['seed'],'method':s['method'],'first_improvement_seconds':positive[0]['elapsed'] if positive else None,
            'first_final_quality_seconds':final[0]['elapsed'] if final else None,'last_commit_seconds':s['last_commit_elapsed'],
            'scheduler_stop_seconds':s['scheduler_stop_elapsed'],'deadline_overshoot_seconds':s['deadline_overshoot_seconds'],'cleanup_seconds':s['cleanup_seconds'],
            **s['physical'],**s['counters']})
    table(ROOT/'anytime_quality.csv',anytime);table(ROOT/'parent_reproduction.csv',parents);table(ROOT/'run_cost_and_mechanism.csv',cost)
    primary=comparisons[0];main=primary.get('delta_control_minus_focal');ci=primary.get('paired_seed_CI95')
    text=['# 完整 GP 相同總時間比較：新增20種子','',f"完成 3 方法 × {n_seeds} 個新增配對種子，每 run 120 秒；新增 LLM 呼叫為 0。輸出先凍結，之後在原批次已查看的30個B實例評估。這是固定方法的種子重複驗證，沒有新增測試實例。",'',
        '## 主要結果','',f"行為 A 相對結構排序的測試平均改善（結構箱數 − A 箱數）為 **{main:.6f} 箱**，配對種子 bootstrap 95% 區間 **[{ci[0]:.6f}, {ci[1]:.6f}]**。" if main is not None else '主配對存在測試失敗，不能刪除失敗後宣稱主要收益。',
        '',
        '| 方法 | 共用測試平均箱數 | 種子平均的標準差 | 平均完成子代數 | 可排序提案數 |','| --- | ---: | ---: | ---: | ---: |']
    for r in summary:text.append(f"| {r['method']} | {r['test_mean_bins']} | {r['test_seed_mean_std']} | {r['mean_offspring_completed']:.1f} | {r['rankable_proposals']} |")
    text+=['','## 全部種子','', '| 種子 | 隨機位置 | 結構排序 | 行為 A | 結構 − A |','| --- | ---: | ---: | ---: | ---: |']
    for k,seed in enumerate(cfg['search_seeds']):
        vals=[float(test_by[m][k].mean()) for m in cfg['methods']]
        text.append(f'| {seed} | {vals[0]:.6f} | {vals[1]:.6f} | {vals[2]:.6f} | {vals[1]-vals[2]:+.6f} |')
    text+=['','## 固定參考','', '| 規則 | 共用測試平均箱數 | 有效實例 |','| --- | ---: | ---: |']
    for r in refs:text.append(f"| {r['heuristic']} | {r['mean_bins']} | {r['valid_instances']}/30 |")
    text+=['','## 解讀與成本','',
        '主要分析單位為配對搜尋種子，30 個實例先在每個種子內平均；不把 600 筆 seed×instance 視為獨立重複。`comparisons.json` 同時提供種子與實例的交叉 bootstrap 敏感性結果。新增20種子為有界擴充，原10已查看；合併30種子的結果屬探索性，不依結果追加或調整模型。',
        '', '線上初始化、載入、試插、探針、排序、完整評估及日誌均在 120 秒截止內。`run_cost_and_mechanism.csv` 保存逐 run 的成本、失敗、重複、可排序機會、父代品質分層與快取使用；committed 計數不含截止中止的最後工作，physical 欄位另保留其啟動及部分結果。終止與收尾的 overshoot 另報，晚完成結果不進入族群。',
        '', '隨機對照同樣使用共同的最多三位置提案，與舊單位置 GP 的分布不同。本輪只檢驗這個共同提案上的選位策略。交叉、基本替換、常數突變、歷史純量／遮罩／根替換仍用原單位置操作，排序器作用範圍與頻率須一起看。',
        '', '搜尋仍使用已看過且 floor 取整的 pilot_dev；共用測試使用官方 round 取整設定。狀態與排序器是先前開發材料，保持凍結，沒有利用共用測試回訓。上游歷史 LLM、片段庫建立與排序器訓練有既有成本，這次零新 LLM 不代表整個研究零生成成本。',
        '', '原始輸出與時間證據：`outputs_freeze.json`、`runs/*/commits`、`runs/*/proposals`、`runs/*/fitness`、`execution_lock.json`。新資料與逐例品質：`test_data_manifest.csv`、`test_nonoverlap_audit.json`、`test_instance_results.csv`。所有種子與陰性結果均保留。']
    (ROOT/'REPORT.md').write_text('\n'.join(text)+'\n',encoding='utf-8')
    x.save(ROOT/'final_summary.json',{'at':x.now(),'primary':primary,'secondary':comparisons[1:],'methods':summary,'references':refs,'new_LLM_calls':0,'search_runs':cfg['runs'],'search_budget_seconds':cfg['nominal_total_search_seconds'],'test':x.load(ROOT/'test_complete.json')})
    print(json.dumps({'primary':primary,'methods':summary}),flush=True)

if __name__=='__main__':
    cmd=sys.argv[1]
    if cmd=='prepare':prepare()
    elif cmd=='worker':test_worker(sys.argv[2],sys.argv[3])
    elif cmd=='evaluate':evaluate()
    elif cmd=='analyze':analyze()
    else:raise ValueError(cmd)
