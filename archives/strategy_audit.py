"""Post-run strategy identification only; no generation or packing evaluations."""
import ast, csv, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
RUN=ROOT/'fragment_gp_limited_01'
sys.path.insert(0,str(RUN))
import cpu as c
import typed_tree as t
import historical_validator as v
import historical_prior as prior
import numpy as np

best=c.load(RUN/'runs/raw_fragment_gp_505/complete.json')['best']
hist=c.load(RUN/'sources/historical_tree_index.json')
sig=prior.signature(best['instances']);ids=hist['behavior'][sig];assert len(ids)==1
old=next(r for r in hist['source_records'] if r['program_id']==ids[0])
new_node=t.parse(best['expression']);old_node=t.parse(old['expression'])
assert isinstance(new_node,ast.BinOp) and isinstance(new_node.op,ast.Mult)
assert isinstance(old_node,ast.UnaryOp) and isinstance(old_node.op,ast.USub)
assert t.key(new_node.left)==t.key(old_node.operand)
assert isinstance(new_node.right,ast.Call) and t.function_name(new_node.right.func)=='np.maximum'
assert len(new_node.right.args)==2 and not new_node.right.keywords
constants=[ast.literal_eval(a) for a in new_node.right.args]
coefficient=max(constants);scale=-coefficient;assert constants==[-100.0,-10.0] and scale==10.0
# Both trees depend only on integer residual r. This legal vector covers r=0..99.
bins=np.arange(1,101,dtype=np.float64);bins.setflags(write=False)
new_values=v.compile_score(t.program(new_node))(1.,bins)
old_values=v.compile_score(t.program(old_node))(1.,bins)
assert np.array_equal(new_values,scale*old_values)
assert np.all(np.isfinite(new_values))
state=c.load(RUN/'runs/raw_fragment_gp_505/checkpoint.json')
first=next(r for r in state['log'] if r['observed_historical_behavior_signature']==sig and r['valid'])
assert first['attempt']==54 and first['mean_bins']==2049.8
eval_initial=c.load(RUN/'initialization/results.json')['505']
from datetime import datetime
init_wall=(max(datetime.fromisoformat(r['evaluation_completed_at']) for r in eval_initial)-min(datetime.fromisoformat(r['evaluation_started_at']) for r in eval_initial)).total_seconds()
other=c.load(RUN/'runs/raw_fragment_gp_404/complete.json')['best']
other_annotation=prior.annotate_result(g_node:=t.parse(other['expression']),other)
assert not other_annotation['historical_tree_program_ids'] and not other_annotation['observed_historical_behavior_program_count']
record={'scope':'read-only strategy identification after the frozen single pilot; no search choices changed',
    'created_at':c.now(),'experiment_manifest_sha256':c.sha((RUN/'manifest.json').read_bytes()),
    'method':'raw_fragment_gp','seed':505,'candidate_id':best['id'],
    'strategy_label':'重新找到既有策略（正比例縮放）','historical_program_id':old['program_id'],
    'new_expression':best['expression'],'historical_expression':old['expression'],
    'new_score_equals_positive_scale_times_old_score':scale,
    'domain':'capacity100, integer item sizes1..100, feasible integer remaining capacities; residual r is integer0..99',
    'algebraic_proof':'Let P=r*(r-25)^2. Historical score=-P; candidate score=P*maximum(-100,-10)=-10P=10*historical score. Positive scaling preserves argmax and all ties. All products have absolute value<=5,625,000<2^53 on the B integer domain, so these float64 integer operations are exact; no overflow/rounding changes the comparison.',
    'complete_pilot_dev_trace_match':True,'all100_possible_residual_scores_match_scale':True,
    'first_new_attempt':54,'first_nominal_slot':70,'dev_mean_bins':best['mean_bins'],
    'gain_vs_initial_best':2066.4-best['mean_bins'],'val_diagnostic_mean_bins':c.load(RUN/'evaluations/pilot_val_final_raw_fragment_gp_505.json')['mean_bins'],
    'first_cumulative_evaluation_seconds':first['cumulative_evaluation_seconds'],
    'first_cumulative_run_seconds':first['cumulative_run_seconds'],
    'first_comparable_wall_seconds_including_shared_init':init_wall+first['cumulative_run_seconds'],
    'other_improved_candidate':{'seed':404,'candidate_id':other['id'],'dev_mean_bins':other['mean_bins'],
        'label':'未匹配支持的歷史樹或完整pilot_dev軌跡；不等於證明全新或泛化更好','source_coverage':'1166/1242 historical programs'},
    'new_candidate_attempts':0,'new_full_packing_evaluations':0,'LLM_requests':0,'score_array_verification_calls':2}
c.save(ROOT/'fragment_gp_limited_strategy_audit.json',record)
lines=['# 有限初始化pilot：策略身分補充稽核','',
    '此稽核只閱讀已封存結果，沒有新增候選、完整裝箱評估、模型或分群，也沒有修改搜尋或封存檔。','',
    '三種子的原始片段GP有2個改善；基本GP／固定父代抽樣均無改善。方法平均dev箱數為2058.8對2066.4，平均改善7.6；診斷val為2062.0對2070.2。這是現有pilot差異，不是新資料的最終結論。','',
    '## 種子505：重新找到既有策略（正比例縮放）','',
    f"歷史來源ID：{old['program_id']}。令r=bins-item，P=r(r-25)²。歷史程式分數−P，新候選分數−10P；新score是舊score的10倍，最高分排序和平手相同。",'',
    '在本實驗容量100／整數物品的域，r為0..99。這些整數浮點運算最大絕對值低於2^53，精確且有限，所以正比例縮放不改決策。兩個程式也已保存相同的完整五例pilot_dev選箱與容量軌跡；另以100個可能剩餘量核對分數比例。這補充了原AST字面比對的限制：字面樹不同，不代表新策略。','',
    f"首次找到在第54個新子代（名義第70格），dev2049.8，較起點少16.6箱；診斷val{record['val_diagnostic_mean_bins']:.1f}。首次成本：累積評估{record['first_cumulative_evaluation_seconds']:.3f}秒，完整run{record['first_cumulative_run_seconds']:.3f}秒；含該seed共用初始化牆鐘{record['first_comparable_wall_seconds_including_shared_init']:.3f}秒。完整歷史根由庫直接插入的禁令已稽核；此候選是由本輪子代組合得來。",'',
    '## 種子404：未匹配支持的歷史','',
    'dev2060.2、診斷val2062.6；未匹配1166個支持歷史程式的完整樹或五例完整軌跡。另76個不支持來源不在樹索引內，不能宣稱已證明全新策略或未見資料優勢。','',
    '研究問題是有限初始化下的搜尋收益：505雖然重找舊策略，從Best-fit起點改善的收益仍有效；不能把它當成新策略發明。404的效果也仍需新的、未參與片段整理或pilot評估的資料確認。本次到1152名義候選停止，未啟動下一輪。','',
    f"原封存manifest SHA256：{record['experiment_manifest_sha256']}。原REPORT.md與final_candidate_labels.json保留AST比對原標籤；本補充給出505的策略等價鑑定，兩者使用的判定標準不同。",'']
(ROOT/'fragment_gp_limited_strategy_audit.md').write_text('\n'.join(lines),encoding='utf-8')
c.save(ROOT/'fragment_gp_limited_strategy_audit_manifest.json',{'created_at':c.now(),'new_candidate_attempts':0,'LLM_requests':0,
    'files':{name:c.sha((ROOT/name).read_bytes()) for name in ['fragment_gp_limited_strategy_audit.py','fragment_gp_limited_strategy_audit.json','fragment_gp_limited_strategy_audit.md']}})
print(json.dumps({k:record[k] for k in ['strategy_label','historical_program_id','first_new_attempt','first_comparable_wall_seconds_including_shared_init']},ensure_ascii=False))
