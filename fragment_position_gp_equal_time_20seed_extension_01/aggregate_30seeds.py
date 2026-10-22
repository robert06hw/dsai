"""Report original10 + requested new20 without changing either search cohort."""
import csv,json,time
from pathlib import Path
import equal_time as x
from evaluate_outputs import table
ROOT=x.ROOT
OLD=ROOT.parent/'fragment_position_gp_equal_time_01'

def csvrows(p):
    with Path(p).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def compare(np,mats,seeds,bootstrap_seed):
    pairs=[('behavior_A_position_gp','structure_position_gp'),('behavior_A_position_gp','uniform_position_gp'),('structure_position_gp','uniform_position_gp')]
    rows=[];n=len(seeds)
    for focal,control in pairs:
        d=mats[control]-mats[focal];valid=bool(np.all(np.isfinite(d)))
        rec={'focal':focal,'control':control,'seeds':n,'all_pairs_valid':valid,'primary':focal=='behavior_A_position_gp' and control=='structure_position_gp'}
        if valid:
            di=d.mean(axis=1);rng=np.random.default_rng(bootstrap_seed)
            boot=di[rng.integers(0,n,(10000,n))].mean(axis=1)
            crossed=[float(d[np.ix_(rng.integers(0,n,n),rng.integers(0,30,30))].mean()) for _ in range(10000)]
            rec.update(delta_control_minus_focal=float(di.mean()),paired_seed_CI95=np.quantile(boot,[.025,.975]).tolist(),crossed_seed_instance_CI95=np.quantile(crossed,[.025,.975]).tolist(),
                median_seed_delta=float(np.median(di)),seed_wins=int((di>0).sum()),seed_ties=int((di==0).sum()),seed_losses=int((di<0).sum()),per_seed_deltas=di.tolist())
        else:rec['note']='Do not omit failed pairs or claim a complete primary win'
        rows.append(rec)
    return rows

def main():
    started=time.perf_counter();x.verify_lock();np,g,t,c,prior,v=x.modules();cfg=x.load(ROOT/'config.json')
    assert x.load(ROOT/'test_complete.json')['nominal_instance_results']==1890
    assert x.sha(ROOT/'test_data/instances.jsonl')==x.sha(OLD/'test_data/instances.jsonl')
    prior_seeds=x.load(OLD/'config.json')['search_seeds'];new_seeds=cfg['search_seeds'];seeds=prior_seeds+new_seeds
    assert len(seeds)==len(set(seeds))==30 and len(new_seeds)==20
    runs=[];observations=[]
    for folder,cohort,expected in [(OLD,'original10',30),(ROOT,'new20',60)]:
        rs=csvrows(folder/'run_results.csv');assert len(rs)==expected
        runs.extend({'cohort':cohort,**r} for r in rs)
        rows=csvrows(folder/'test_instance_results.csv')
        observations.extend({'cohort':cohort,**r} for r in rows if r['role']=='frozen_GP_output')
    assert len(runs)==90 and len({(r['seed'],r['method']) for r in runs})==90
    assert len(observations)==2700
    original_refs=[r for r in csvrows(OLD/'test_instance_results.csv') if r['role']=='fixed_reference']
    current_refs=[r for r in csvrows(ROOT/'test_instance_results.csv') if r['role']=='fixed_reference']
    oldref={(r['heuristic'],r['instance_id']):r for r in original_refs};newref={(r['heuristic'],r['instance_id']):r for r in current_refs}
    assert len(oldref)==len(newref)==90 and set(oldref)==set(newref)
    for key in oldref:
        for field in ['valid','bins_used','trace_hash','chosen_capacity_hash']:assert oldref[key].get(field)==newref[key].get(field),(key,field)
    observations.extend({'cohort':'fixed_reference',**r} for r in original_refs);assert len(observations)==2790
    agg=ROOT/'aggregate';agg.mkdir(exist_ok=True)
    table(agg/'all30_threemethod_run_summary.csv',runs)
    table(agg/'all30_threemethod_B_instance_results.csv',observations)
    ids=sorted({r['instance_id'] for r in observations});assert len(ids)==30
    matrices={};summary=[]
    for method in cfg['methods']:
        a=[]
        for seed in seeds:
            rs={r['instance_id']:r for r in observations if r['method']==method and r['search_seed']==str(seed)}
            assert set(rs)==set(ids)
            a.append([float(rs[i]['bins_used']) if rs[i]['valid']=='True' else float('nan') for i in ids])
        matrices[method]=np.asarray(a)
        for cohort,indices in [('original10',np.arange(10)),('new20',np.arange(10,30)),('all30',np.arange(30))]:
            matrix=matrices[method][indices];runrows=[r for r in runs if r['method']==method and (cohort=='all30' or r['cohort']==cohort)]
            valid=bool(np.all(np.isfinite(matrix)))
            summary.append({'cohort':cohort,'method':method,'seeds':len(indices),'test_valid_instances':int(np.isfinite(matrix).sum()),
                'test_mean_bins':float(matrix.mean()) if valid else None,'test_seed_mean_std':float(matrix.mean(axis=1).std(ddof=1)) if valid else None,
                'test_seed_median_bins':float(np.median(matrix.mean(axis=1))) if valid else None,
                'dev_mean_bins':float(np.mean([float(r['dev_final']) for r in runrows])) if all(r['dev_final'] for r in runrows) else None,
                'mean_completed_offspring':float(np.mean([int(r['offspring_completed']) for r in runrows])),
                'rankable_proposals':sum(int(r['rankable_proposals']) for r in runrows)})
    comparisons={}
    for cohort,indices in [('original10',np.arange(10)),('new20',np.arange(10,30)),('all30',np.arange(30))]:
        comparisons[cohort]=compare(np,{m:a[indices] for m,a in matrices.items()},[seeds[i] for i in indices],2026101812)
    table(agg/'all30_threemethod_method_summary.csv',summary);x.save(agg/'all30_threemethod_comparisons.json',comparisons)
    wide=[]
    for k,seed in enumerate(seeds):
        row={'seed':seed,'cohort':'original10' if k<10 else 'new20'}
        for m in cfg['methods']:row[m]=float(matrices[m][k].mean()) if np.all(np.isfinite(matrices[m][k])) else None
        row['delta_structure_minus_A']=row['structure_position_gp']-row['behavior_A_position_gp'] if row['structure_position_gp'] is not None and row['behavior_A_position_gp'] is not None else None
        wide.append(row)
    table(agg/'all30_paired_seed_results.csv',wide)
    curves=[];costs=[];parents=[]
    for folder,cohort in [(OLD,'original10'),(ROOT,'new20')]:
        curves.extend({'cohort':cohort,**r} for r in csvrows(folder/'anytime_quality.csv'))
        costs.extend({'cohort':cohort,**r} for r in csvrows(folder/'run_cost_and_mechanism.csv'))
        parents.extend({'cohort':cohort,**r} for r in csvrows(folder/'parent_reproduction.csv'))
    table(agg/'all30_anytime_quality.csv',curves);table(agg/'all30_run_cost_and_mechanism.csv',costs);table(agg/'all30_parent_reproduction.csv',parents)
    primary=comparisons['all30'][0];delta=primary.get('delta_control_minus_focal');ci=primary.get('paired_seed_CI95')
    text=['# 等總時間GP：原10＋新增20種子，合計30種子','',
        '三方法各30種子，共90 runs，每run120秒。新增批次60 runs的名義搜尋上限7200秒，兩批合計10800秒；準備、程序收尾、測試、分析與稽核成本另列。沒有新增LLM呼叫、模型或回訓。',
        '', '原10種子結果已查看後，使用者再要求增加20種子。方法保持凍結。測試是同一30個B實例，沒有新增任務實例。',
        '', '## 主要對比','',
        f'全30種子「結構箱數−行為A箱數」平均為 **{delta:.6f}箱**，配對種子bootstrap95%區間 **[{ci[0]:.6f}, {ci[1]:.6f}]**。正值表示A較好。' if delta is not None else '主要對比存在失敗配對，不能刪除失敗後宣稱主要勝出。',
        '', '| 批次 | 方法 | 種子數 | 共用測試平均箱數 | 種子平均標準差 | 平均完成子代 |','| --- | --- | ---: | ---: | ---: | ---: |']
    for r in summary:text.append(f"| {r['cohort']} | {r['method']} | {r['seeds']} | {r['test_mean_bins']} | {r['test_seed_mean_std']} | {r['mean_completed_offspring']:.1f} |")
    text+=['','## 各批次配對差異','', '| 批次 | 對比（控制−方法） | 平均差 | 種子95%區間 | 勝／平／負 |','| --- | --- | ---: | --- | --- |']
    for cohort,rs in comparisons.items():
        for r in rs:text.append(f"| {cohort} | {r['control']} − {r['focal']} | {r.get('delta_control_minus_focal')} | {r.get('paired_seed_CI95')} | {r.get('seed_wins')}/{r.get('seed_ties')}/{r.get('seed_losses')} |")
    text+=['','## 全30種子','', '| 批次 | 種子 | 隨機位置 | 結構 | 行為A | 結構−A |','| --- | --- | ---: | ---: | ---: | ---: |']
    for r in wide:text.append(f"| {r['cohort']} | {r['seed']} | {r['uniform_position_gp']} | {r['structure_position_gp']} | {r['behavior_A_position_gp']} | {r['delta_structure_minus_A']} |")
    text+=['','## 資料與限制','',
        '主要分析單位為配對搜尋種子；每個種子先平均30例，再對30個種子等權平均。不能將900筆seed×instance當獨立重複。交叉重抽種子與實例的敏感性區間見JSON。所有種子、失敗、重複、超限與截止都保留，不依正例補抽。',
        '', '原10與新20的執行時間批次不同，均在相同120秒截止與單run／單worker設定下比較。每批內配對方法，另外報批次分層結果與實際成本，不能僅由完成候選數宣稱硬體固有速度差。',
        '', '初始化、試插、探針、排序、評估與記錄皆計入run。候選計數可受120秒內各操作耗時影響。committed成本與計數不含截止中止的最後一部分，但整段120秒仍收費；原始部分結果保留在各run。',
        '', '逐例合併表2790列包含90個搜尋輸出×30例與三個參考各30例。兩批參考箱數及決策雜湊一致，參考僅列一次。原10來源檔保持封存，不改寫。新增20詳細報告見上一層REPORT.md。']
    (agg/'REPORT_all30.md').write_text('\n'.join(text)+'\n',encoding='utf-8')
    audit={'at':x.now(),'passed':True,'seeds':30,'runs':90,'original_seed_count':10,'new_seed_count':20,'test_instance_rows':2790,
        'shared_instances':30,'new_test_instances':0,'fixed_reference_rows':90,'reference_bins_and_trace_hashes_match':True,'no_duplicate_search_seed_or_run':True,
        'bootstrap_seed':2026101812,'bootstrap_draws':10000,'original_manifest_sha256':x.sha(OLD/'manifest.json'),'new_LLM_calls':0,'aggregation_wall_seconds':time.perf_counter()-started}
    x.save(agg/'aggregation_audit.json',audit)
    print(json.dumps({'aggregate_seeds':30,'aggregate_runs':90,'instance_rows':2790,'primary':primary}),flush=True)

if __name__=='__main__':main()
