"""Evaluate frozen new outputs on existing B and combine all 20 search seeds."""
import concurrent.futures,csv,datetime,hashlib,json,os,subprocess,sys,time,warnings
from pathlib import Path
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1';os.environ['MKL_NUM_THREADS']='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
import numpy as np
import cpu as c
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'aggregate'
OLD=ROOT.parent/'fragment_gp_limited_01'
TEST=ROOT.parent/'fragment_gp_limited_test_01'
NEW=list(range(606,2223,101));ORIGINAL=[303,404,505];ALL=ORIGINAL+NEW
METHODS=['basic_gp','raw_fragment_gp','fixed_parent_random']
def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):
    p=Path(p);p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def table(name,rows):c.table(OUT/name,rows)
def check():
    for p,h in load(OUT/'pre_B_lock.json')['files'].items():assert sha(ROOT/p)==h,p
def prepare():
    assert not (OUT/'pre_B_lock.json').exists(),'Cannot refreeze final outputs'
    assert load(ROOT/'search_complete.json')['runs']==51
    assert load(ROOT/'audit_checks.json')['passed']
    original_manifest=load(TEST/'manifest.json')
    assert sha(TEST/'manifest.json')==load(ROOT/'sources/extension_change_record.json')['original_test_manifest_sha256']
    for r in original_manifest['artifacts']:assert sha(TEST/r['path'])==r['sha256'],r['path']
    assert sha(ROOT/'data/reused_B.jsonl')==sha(TEST/'data/test_B.jsonl')
    registry=[]
    for seed in NEW:
        for method in METHODS:
            name=f'{method}_{seed}';file=f'final_candidates/{name}.py'
            registry.append({'heuristic':name,'method':method,'search_seed':seed,'file':file,'sha256':sha(ROOT/file)})
    OUT.mkdir(exist_ok=True)
    save(OUT/'program_registry.json',registry)
    save(OUT/'scope.json',{'original_seeds':ORIGINAL,'additional_seeds':NEW,'all_seeds':ALL,'new_programs':51,
       'new_B_full_instance_evaluations':1530,'old_B_evaluations_reused':360,'combined_B_rows':1890,
       'data_role':'Same already-viewed B30, not a new holdout. Additional search seeds requested after observing original results.',
       'methods_unchanged':True,'selection':'prior pilot_dev best; all51 searches ended and search audit passed before B evaluation',
       'new_search_nominal_slots':6528,'combined_search_nominal_slots':7680,'new_physical_candidate_attempts':5984,
       'combined_physical_candidate_attempts':7040,'LLM_requests':0,
       'bootstrap':'Crossed paired seed and instance bootstrap,10000 replicates,PCG64(900002). Resample20 seeds and30 instances independently, use Cartesian crossing and identical draws across methods. Descriptive after post-result extension.'})
    # Reuse saved scores and original packing traces, no old program execution.
    old_rows=list(csv.DictReader((TEST/'instance_results.csv').open(encoding='utf-8-sig')))
    assert len(old_rows)==360
    table('original_B_instance_results.csv',old_rows)
    old_search=list(csv.DictReader((OLD/'run_summary.csv').open(encoding='utf-8-sig')))
    new_search=list(csv.DictReader((ROOT/'run_summary.csv').open(encoding='utf-8-sig')))
    assert len(old_search)==9 and len(new_search)==51
    table('all20_search_run_summary.csv',old_search+new_search)
    paths=[ROOT/'aggregate_extension.py',ROOT/'cpu.py',ROOT/'data/reused_B.jsonl',ROOT/'manifest.json',
           OUT/'program_registry.json',OUT/'scope.json',OUT/'original_B_instance_results.csv',OUT/'all20_search_run_summary.csv']
    paths += [ROOT/r['file'] for r in registry]
    save(OUT/'pre_B_lock.json',{'locked_at':c.now(),'all51_outputs_frozen':True,
       'files':{p.relative_to(ROOT).as_posix():sha(p) for p in paths},
       'reused_original_test_manifest_sha256':sha(TEST/'manifest.json')})
    print('B expansion locked: 51 frozen outputs x same30 instances =1530 new full evaluations; old360 reused.',flush=True)
def worker(name):
    check();limit=c.memory_limit();reg=next(r for r in load(OUT/'program_registry.json') if r['heuristic']==name)
    ns={'np':np};exec(compile((ROOT/reg['file']).read_text(encoding='utf-8'),name,'exec'),ns)
    instances=[json.loads(s) for s in (ROOT/'data/reused_B.jsonl').read_text(encoding='utf-8').splitlines()]
    rows=[];traces={};begin=time.perf_counter()
    for inst in instances:
        record={'dataset':'B_fresh','instance_id':inst['id'],'instance_seed':inst['seed'],'heuristic':name,
          'method':reg['method'],'search_seed':reg['search_seed'],'bins_used':None,'runtime':None,'cpu_seconds':None,
          'trace_hash':'','chosen_capacity_hash':'','error':'','warnings':[]}
        start=time.perf_counter()
        with warnings.catch_warnings(record=True) as ws:
            warnings.simplefilter('once')
            try:
                result,ix,caps=c.pack(inst,ns['score'])
                record.update({k:result[k] for k in ['bins_used','runtime','cpu_seconds','trace_hash','chosen_capacity_hash']})
                traces[inst['id']+'_choices']=ix;traces[inst['id']+'_capacities']=caps
            except Exception as e:record.update(error=f'{type(e).__name__}: {e}',runtime=time.perf_counter()-start)
        record['warnings']=sorted({str(w.message) for w in ws});rows.append(record)
    (OUT/'traces').mkdir(exist_ok=True);np.savez_compressed(OUT/'traces'/f'{name}.npz',**traces)
    save(OUT/'results'/f'{name}.json',{'heuristic':name,'rows':rows,'resource_limit':limit,
        'worker_wall_seconds':time.perf_counter()-begin,'completed_at':c.now(),'complete_instance_attempts':30})
def invoke(name):
    path=OUT/'results'/f'{name}.json';assert not path.exists(),'No retries of a completed B program'
    start=time.perf_counter();p=subprocess.run([sys.executable,str(ROOT/'aggregate_extension.py'),'worker',name],
           capture_output=True,text=True,encoding='utf-8',timeout=120)
    if p.returncode:raise RuntimeError(name+': '+p.stderr[-1500:])
    result=load(path);result['subprocess_wall_seconds']=time.perf_counter()-start;save(path,result);return result
def evaluate():
    check();assert not (OUT/'B_started.json').exists(),'No automatic full evaluation retries'
    registry=load(OUT/'program_registry.json');save(OUT/'B_started.json',{'started_at':c.now(),'new_full_instance_evaluations':1530})
    (OUT/'results').mkdir(exist_ok=True);start=time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures=[pool.submit(invoke,r['heuristic']) for r in registry]
        for n,f in enumerate(concurrent.futures.as_completed(futures),1):
            result=f.result()
            if n%5==0 or n==51:print(f'New B programs {n}/51; elapsed={time.perf_counter()-start:.1f}s; errors={sum(bool(r["error"]) for r in result["rows"])}',flush=True)
    save(OUT/'B_complete.json',{'completed_at':c.now(),'new_complete_instance_evaluations':1530,'wall_seconds':time.perf_counter()-start,
        'old_programs_reexecuted':0,'LLM_requests':0,'no_B_selection':True})
def analyze():
    check();assert not (OUT/'manifest.json').exists(),'Already sealed, use verify'
    regs=load(OUT/'program_registry.json');new_results=[load(OUT/'results'/f'{r["heuristic"]}.json') for r in regs]
    new_rows=[{**r,'warnings':json.dumps(r['warnings'])} for result in new_results for r in result['rows']]
    assert len(new_rows)==1530
    table('new17_B_instance_results.csv',new_rows)
    previous=list(csv.DictReader((OUT/'original_B_instance_results.csv').open(encoding='utf-8-sig')))
    for r in previous:
        for k in ['bins_used','instance_seed']:r[k]=int(r[k])
        for k in ['runtime','cpu_seconds']:r[k]=float(r[k])
        r['search_seed']=int(r['search_seed']) if r['search_seed'] else None
    rows=previous+new_rows;assert len(rows)==1890
    table('all20_B_instance_results.csv',rows)
    errors=[r for r in rows if r['error']]
    if errors:
        table('B_errors.csv',errors)
        (OUT/'REPORT.md').write_text('B評估完成，但有錯誤。全部錯誤保存B_errors.csv；不丟棄失敗或重選候選。平均品質比較暫不計算。',encoding='utf-8')
        raise RuntimeError('B error rows preserved; primary quality comparison cannot drop failures')
    matrix={}
    for r in rows:matrix.setdefault(r['heuristic'],{})[r['instance_id']]=r
    ids=list(matrix['Best-fit']);assert len(ids)==30 and len(matrix)==63
    assert all(len(v)==30 for v in matrix.values())
    B={m:np.asarray([[matrix[f'{m}_{s}'][i]['bins_used'] for i in ids] for s in ALL],dtype=float) for m in METHODS}
    bf=np.asarray([matrix['Best-fit'][i]['bins_used'] for i in ids],dtype=float)
    summaries=[]
    search=list(csv.DictReader((OUT/'all20_search_run_summary.csv').open(encoding='utf-8-sig')))
    for m in METHODS:
        for seed,values in zip(ALL,B[m]):
            sr=next(r for r in search if r['method']==m and int(r['seed'])==seed)
            delta=bf-values
            summaries.append({'method':m,'seed':seed,'cohort':'original3' if seed in ORIGINAL else 'additional17',
               'B_mean_bins':float(values.mean()),'B_delta_vs_Best_fit':float(delta.mean()),
               'B_wins_vs_Best_fit':int(np.sum(delta>0)),'B_ties_vs_Best_fit':int(np.sum(delta==0)),
               'B_losses_vs_Best_fit':int(np.sum(delta<0)),'dev_initial':float(sr['initial_best_dev']),
               'dev_final':float(sr['final_dev']),'dev_gain_vs_initial':float(sr['gain_vs_initial_best']),
               'pilot_val_diagnostic':float(sr['final_val_diagnostic']),'first_final_quality_new_attempt':int(sr['first_final_quality_new_attempt']),
               'search_comparable_wall_seconds':float(sr['comparable_run_wall_seconds']),
               'final_historical_tree_class':sr['final_historical_tree_class']})
    table('all20_run_summary.csv',summaries)
    cohort_rows=[]
    for cohort,mask in [('original3',np.arange(20)<3),('additional17',np.arange(20)>=3),('all20',np.ones(20,dtype=bool))]:
        for m in METHODS:
            seedmeans=B[m][mask].mean(axis=1)
            sr=[r for r in summaries if r['method']==m and (cohort=='all20' or r['cohort']==cohort)]
            cohort_rows.append({'cohort':cohort,'method':m,'search_seeds':int(mask.sum()),'B_instances':30,
               'B_mean_bins':float(seedmeans.mean()),'B_delta_vs_Best_fit':float(bf.mean()-seedmeans.mean()),
               'B_seed_SD':float(seedmeans.std(ddof=1)),'B_seed_min':float(seedmeans.min()),'B_seed_max':float(seedmeans.max()),
               'mean_dev_final':float(np.mean([r['dev_final'] for r in sr])),
               'mean_dev_gain_vs_initial':float(np.mean([r['dev_gain_vs_initial'] for r in sr])),
               'mean_pilot_val_diagnostic':float(np.mean([r['pilot_val_diagnostic'] for r in sr])),
               'mean_search_comparable_wall_seconds':float(np.mean([r['search_comparable_wall_seconds'] for r in sr]))})
    table('method_cohort_summary.csv',cohort_rows)
    paired=[];paired_instances=[];intervals=[]
    rng=np.random.Generator(np.random.PCG64(900002));seed_draws=rng.integers(0,20,size=(10000,20));instance_draws=rng.integers(0,30,size=(10000,30))
    for ctrl in ['basic_gp','fixed_parent_random']:
        D=B[ctrl]-B['raw_fragment_gp']
        for row,seed in enumerate(ALL):
            ds=D[row];paired.append({'control':ctrl,'seed':seed,'cohort':'original3' if seed in ORIGINAL else 'additional17',
               'mean_delta_control_minus_raw':float(ds.mean()),'raw_wins_instances':int(np.sum(ds>0)),
               'ties_instances':int(np.sum(ds==0)),'raw_losses_instances':int(np.sum(ds<0))})
            for i,d in zip(ids,ds):paired_instances.append({'control':ctrl,'seed':seed,'instance_id':i,'delta_control_minus_raw':int(d)})
        bootstrap=D[seed_draws[:,:,None],instance_draws[:,None,:]].mean(axis=(1,2));lo,hi=np.quantile(bootstrap,[.025,.975])
        for cohort,mask in [('original3',np.arange(20)<3),('additional17',np.arange(20)>=3),('all20',np.ones(20,dtype=bool))]:
            ds=D[mask].mean(axis=1)
            intervals.append({'control':ctrl,'cohort':cohort,'seeds':int(mask.sum()),'mean_delta_control_minus_raw':float(ds.mean()),
               'raw_wins_seeds':int(np.sum(ds>0)),'ties_seeds':int(np.sum(ds==0)),'raw_losses_seeds':int(np.sum(ds<0)),
               'crossed_bootstrap_95_low':float(lo) if cohort=='all20' else None,
               'crossed_bootstrap_95_high':float(hi) if cohort=='all20' else None})
    table('paired_seed_differences.csv',paired);table('paired_instance_differences.csv',paired_instances);table('paired_cohort_summary.csv',intervals)
    refs=[{'heuristic':m,'B_mean_bins':float(np.mean([matrix[m][i]['bins_used'] for i in ids]))} for m in ['Best-fit','EoH','Historical-best']]
    table('fixed_reference_summary.csv',refs)
    # Rehash every new full decision trace. No extra packing or model call.
    traces_checked=0
    for result in new_results:
        assert result['resource_limit']['enforced']
        with np.load(OUT/'traces'/f'{result["heuristic"]}.npz') as traces:
            for r in result['rows']:
                ix=traces[r['instance_id']+'_choices'];caps=traces[r['instance_id']+'_capacities']
                assert ix.shape==caps.shape==(5000,) and int(ix.max())+1==r['bins_used']
                assert hashlib.sha256(ix.astype('<i4').tobytes()).hexdigest()==r['trace_hash']
                assert hashlib.sha256(caps.astype('<i2').tobytes()).hexdigest()==r['chosen_capacity_hash'];traces_checked+=1
    assert traces_checked==1530
    completion=load(OUT/'B_complete.json');save(OUT/'audit_checks.json',{'passed':True,'all20_seed_results_reported':True,
       'new1530_full_trace_hashes_checked':True,'no_test_reselection':True,'same_frozen_B30':True,'errors':0,
       'original360_reused_without_reexecution':True,'new_outputs51':True,'newLLM_requests':0,
       'all_search_algorithms_unchanged':load(ROOT/'sources/extension_change_record.json')['unchanged_search_function_ASTs'],
       'post_result_extension_and_reused_test_disclosed':True})
    save(OUT/'cost_summary.json',{'new_search_nominal_slots':6528,'all20_nominal_slots':7680,
       'new_physical_candidate_attempts':5984,'all20_physical_candidate_attempts':7040,
       'new_B_full_instance_evaluations':1530,'all_B_result_rows':1890,'new_B_wall_seconds':completion['wall_seconds'],
       'new_search_and_pilot_diagnostics_wall_seconds':load(ROOT/'cost_summary.json')['experiment_wall_seconds'],
       'LLM_requests':0,'LLM_tokens':0})
    lines=['# 有限初始化歷史片段GP：20搜尋種子擴充比較','',
       '原3種子303／404／505保持封存，新增17種子606–2222（步長101）。三方法、128名額、共享初始化與全部搜尋設定不變。新增6528名義名額／5984實體嘗試；合計7680名義／7040實體。零LLM／新模型／分群。','',
       '此擴充是看到原3種子與B結果後依使用者要求執行；同一30例B已查看，僅作一致的擴充種子比較，不宣稱新未看測試確認。新51輸出都只以pilot_dev決定，全部搜尋結束並稽核後才評B，不重選、不修改程式。','',
       '## 原3、新17與全部20的主要比較','',
       '| 種子範圍 | 方法 | B平均箱數 | 相對Best-fit少用箱數 | 種子平均SD | 平均dev | 平均診斷val |','|---|---|---:|---:|---:|---:|---:|']
    for r in cohort_rows:lines.append(f'| {r["cohort"]} | {r["method"]} | {r["B_mean_bins"]:.3f} | {r["B_delta_vs_Best_fit"]:.3f} | {r["B_seed_SD"]:.3f} | {r["mean_dev_final"]:.3f} | {r["mean_pilot_val_diagnostic"]:.3f} |')
    lines+=['','Δ＝對照箱數−片段GP箱數，正值表示片段GP较好。勝平負以每個搜尋種子的相同30例平均為單位，不只計505。','',
       '| 對照 | 範圍 | 平均Δ | 片段GP種子勝／平／負 | 20種子×30例交叉bootstrap95% |','|---|---|---:|---:|---:|']
    for r in intervals:
        ci=f'[{r["crossed_bootstrap_95_low"]:.3f}, {r["crossed_bootstrap_95_high"]:.3f}]' if r['cohort']=='all20' else '—'
        lines.append(f'| {r["control"]} | {r["cohort"]} | {r["mean_delta_control_minus_raw"]:.3f} | {r["raw_wins_seeds"]}/{r["ties_seeds"]}/{r["raw_losses_seeds"]} | {ci} |')
    lines+=['','交叉bootstrap每次獨立有放回抽20搜尋種子與30實例，取交叉矩陣平均，三方法共用抽樣；10000次、PCG64(900002)。這反映觀察樣本的兩個變異來源，避免把600笔種子×實例當獨立；事後擴充與已查看B的限制仍在。','',
       '## 全部20種子（平均B箱數）','',
       '| seed | 基本GP | 原始片段GP | 固定父代片段抽樣 | 片段對基本Δ | 片段對固定Δ |','|---|---:|---:|---:|---:|---:|']
    for n,seed in enumerate(ALL):
        basic,raw,fixed=(B[m][n].mean() for m in METHODS)
        lines.append(f'| {seed} | {basic:.3f} | {raw:.3f} | {fixed:.3f} | {basic-raw:.3f} | {fixed-raw:.3f} |')
    lines+=['','## 固定參考與成本','']
    for ref in refs:lines.append(f'{ref["heuristic"]}：B平均{ref["B_mean_bins"]:.3f}箱。')
    lines+=['',
       '歷史最佳只作固定參考；既有策略的重新找到仍是有限初始化收益，不能算新策略發明。原505已證明為歷史多項式正比例縮放；新增輸出的字面／保守規範化歷史匹配与首次找到成本由搜尋日志照實保留，有限pilot軌跡相同不代表普遍等價。','',
       f'新增搜尋與pilot診斷牆鐘{load(ROOT/"cost_summary.json")["experiment_wall_seconds"]:.3f}秒；新增1530次B完整評估牆鐘{completion["wall_seconds"]:.3f}秒，全部有效。既有360筆B結果直接沿用，總表1890筆。單run可比搜尋時間（含該seed共享初始化）保存在all20_run_summary.csv，總牆鐘與并行工作加總不可混同。','',
       '30例B容量100／5000物品、官方Weibull3×45、clip1..100、np.round，種子800001–800030與原SHA完全相同；pilot为floor版且已查看。未生成新B資料。','',
       '- all20_run_summary.csv：60run全部品質、成本與標籤。',
       '- method_cohort_summary.csv：原3／新17／全部20三組方法摘要。',
       '- paired_seed_differences.csv、paired_cohort_summary.csv：兩個主要搜尋對照之全部種子差異。',
       '- all20_B_instance_results.csv：1890筆逐例結果；其中1530筆新增、360筆重用。',
       '- traces/：51支新候選、1530次B完整軌跡；原360軌跡仍在原封存。',
       '- pre_B_lock.json：51最終輸出與資料在B評估前凍結；audit_checks.json記完整核對。','']
    (OUT/'REPORT.md').write_text('\n'.join(lines),encoding='utf-8')
    files=[p for p in sorted(OUT.rglob('*')) if p.is_file() and p!=OUT/'manifest.json']
    save(OUT/'manifest.json',{'sealed_at':c.now(),'new_B_full_evaluations':1530,'all_B_rows':1890,
       'files':{p.relative_to(OUT).as_posix():sha(p) for p in files}})
    print(json.dumps({'cohorts':cohort_rows,'paired':intervals,'new_B_evaluations':1530,'all_B_rows':1890},ensure_ascii=False),flush=True)
def verify():
    check()
    for p,h in load(OUT/'manifest.json')['files'].items():assert sha(OUT/p)==h,p
    assert load(OUT/'audit_checks.json')['passed']
    print('Verified complete 20-seed aggregate; 1530 new B evaluations,1890 total rows,zero LLM.',flush=True)
if __name__=='__main__':
    mode=sys.argv[1]
    if mode=='prepare':prepare()
    elif mode=='evaluate':evaluate()
    elif mode=='worker':worker(sys.argv[2])
    elif mode=='analyze':analyze()
    elif mode=='verify':verify()
    else:raise ValueError(mode)
