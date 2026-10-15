def report(config,summaries,grouped,initial_rows,cost,reference_dev_by_id,val_by_id,rediscovery_rows):
    lines=['# 匹配隨機片段GP：原30種子配對對照','',
    '沿用既有30種子與480個共同初始化名額；每run16初始化＋112新子代，共3840名義名額、3360次新候選嘗試。初始程式／評估／算子順序完全重用且核對原封存。全部失敗、超限與重複均計入；零LLM。','',
    '只新增matched_random_fragment_gp；其父代更新、算子RNG、比例、大小限制、評估及精英選拔與原始片段GP一致。隨機庫1240個唯一AST，每個歷史可抽樣位置精確匹配輸出型別、節點數及深度，包含原30個超限片段位置。','',
    '常數與算子頻率、語意難度未匹配；只用有限數值／形狀接口探針篩選隨機庫，未依裝箱品質篩选。單一隨機庫（種子918273645），不能代表所有可能隨機庫。候選仍採原完整裝箱合法性與品質標準。','',
    '| seed | 初始dev | 最終dev | 改善 | 已看val診斷 | 有效／112 | 重複 | 最終节点／深度 | 首達最終品質 |','|---|---:|---:|---:|---:|---:|---:|---|---:|']
    for r in summaries:
        lines.append(f'| {r["seed"]} | {r["initial_best_dev"]:.1f} | {r["final_dev"]:.1f} | {r["gain_vs_initial_best"]:.1f} | {r["final_val_diagnostic"]:.1f} | {r["valid_new"]} | {r["duplicate_new"]} | {r["final_nodes"]}/{r["final_depth"]} | {r["first_final_quality_new_attempt"]} |')
    lines+=['',f'新增搜尋與pilot診斷牆鐘{cost["experiment_wall_seconds"]:.3f}秒；另計建庫{cost["bank_build_wall_seconds"]:.3f}秒。初始化實體新增成本為0；各run可比成本仍加原同seed共同初始化時間，保持與舊方法的成本口徑。四worker，各512MiB／120秒、BLAS1。','',
    '全部搜尋結束後才評已看pilot_val；最終程式只以pilot_dev選出。B30凍結比較見aggregate/REPORT.md。已查看B、事後新增方法、單一隨機庫的限制需保留。','',
    'attempt_results.csv、parent_reproduction.csv、checkpoint與traces保存全部子代、父代、完整裝箱決策；run_summary.csv及candidate_size_summary.csv保存有效率與大小。來源分析見封存fragment_gp_mechanism_30seed_01。','']
    return '\n'.join(lines)
