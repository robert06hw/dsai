"""Descriptive pilot report for the unchanged-method seed extension."""
def report(config,summaries,grouped,initial_rows,cost,reference_dev_by_id,val_by_id,rediscovery_rows):
    seeds=config['seeds'];n=len(seeds)
    lines=['# 有限初始化GP：追加10個搜尋種子','',
        f'三方法×{n}個新種子×128＝{config["nominal_total"]}名義名額；共用初始化{16*n}次、子代{112*3*n}次、合計實體候選{16*n+112*3*n}。每run16初始化＋112新子代。全部失敗、超限與重複計入；有效重複仍重新完整評估。零LLM／新模型／新分群。','',
        '種子：'+', '.join(map(str,seeds))+'。既有20種子結果封存並另行合併，不重跑。此為已看到既有20種子與B結果後，依使用者要求進行的種子擴充；不是事前鎖定的30種子確認實驗。','',
        '初始化保持Best-fit＋15個基本算子隨機表達式，三方法逐项共用；原始庫1947個、合法視圖1240個與707個完整根禁用完全固定，沒有加入新的完整歷史好程式。交叉56／替換39／常數突變17、完整展開64操作節點／8層、族群上限16、父代均勻與精英選拔皆不變。','',
        '## 新增run完整pilot結果','',
        '| 方法 | seed | 初始dev | 最終dev | dev改善 | 已查看val診斷 | 有效／112 | 首達新子代 |','|---|---:|---:|---:|---:|---:|---:|---:|']
    for r in summaries:
        lines.append(f'| {r["method"]} | {r["seed"]} | {r["initial_best_dev"]:.1f} | {r["final_dev"]:.1f} | {r["gain_vs_initial_best"]:.1f} | {r["final_val_diagnostic"]:.1f} | {r["valid_new"]} | {r["first_final_quality_new_attempt"]} |')
    lines+=['','## 新增10種子方法平均','',
        f'| 方法 | 平均dev | 平均相對初始化改善 | 平均診斷val | 改善run／{n} | 有效子代／{112*n} | 可比run牆鐘秒 |','|---|---:|---:|---:|---:|---:|---:|']
    for r in grouped:
        lines.append(f'| {r["method"]} | {r["mean_final_dev"]:.3f} | {r["mean_gain_vs_initial"]:.3f} | {r["mean_final_val_diagnostic"]:.3f} | {r["runs_improved_initial"]} | {r["valid_new_total"]} | {r["mean_comparable_run_wall_seconds"]:.3f} |')
    lines+=['','pilot_dev／pilot_val仍是原floor版五例，各容量100、5000物品；既有30例B是官方round設定且已查看。搜尋選拔只使用pilot_dev，全部30run完成後才做val及B評估。固定參考不作父代或搜尋成果。','',
        '## 費用、標籤與稽核','',
        f'搜尋與pilot診斷完整牆鐘{cost["experiment_wall_seconds"]:.3f}秒；共用初始化實體成本只計一次，各run可比成本加該seed共同初始化時間。新增pilot診斷43個val候選與3個dev參考，分開記錄。四worker、各512MiB／120秒、BLAS1。','',
        '歷史既有策略標籤：完整AST或保守規範化樹匹配可標重找；完整pilot軌跡匹配僅為有限資料相同行為。不匹配支持的1166個來源不能證明策略全新。已知505正比例縮放的補充鑑定保留在原三種子資料，不因此刪庫或改選拔。','',
        'attempt_results.csv完整記錄3360子代；run_summary.csv記30run；quality_curves.csv、parent_reproduction.csv、first_rediscovery_costs.csv及traces/保存成本、族群與軌跡。原資料、完整根禁令、算子順序、父代固定／更新、初始化與兩次鎖定皆由analyze.py重播稽核。','',
        '30種子及同一30例B的合併比較將另存aggregate/，區分既有20種子、新10種子與合計30種子，不能只挑改善的種子。後續不因結果追加名額或重選輸出。','']
    return '\n'.join(lines)
