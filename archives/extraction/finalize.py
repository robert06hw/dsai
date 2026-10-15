"""Reporting, independent artifact audit and library freeze; never generates/evolves."""
import ast, collections, csv, json, shutil, sys, time
from pathlib import Path
import cpu as c
import typed_tree as t
from pipeline import save, check_lock, ARCHIVES
import numpy as np
ROOT=Path(__file__).resolve().parent

def table(path,rows):
    c.table(ROOT/path,rows)

def tree_payload(node):
    out={'node':type(node).__name__,'type':t.infer(node),'key':t.key(node)}
    if isinstance(node,(ast.Name,ast.Constant,ast.Attribute,ast.Subscript)):out['expression']=t.text(node)
    if isinstance(node,(ast.BinOp,ast.UnaryOp)):out['operator']=type(node.op).__name__
    if isinstance(node,ast.Compare):out['operators']=[type(op).__name__ for op in node.ops]
    if isinstance(node,ast.Call):
        out['callable']=t.function_name(node.func)
        out['keywords']=[{'name':kw.arg,'value':t.text(kw.value)} for kw in node.keywords]
    out['children']=[{'field':field,'index':index,'tree':tree_payload(child)} for (field,index),child in t.child_fields(node)]
    return out

def verify(root):
    root=Path(root).resolve();m=c.load(root/'manifest.json');total=0
    for row in m['artifacts']:
        p=(root/row['path']).resolve();assert p.is_relative_to(root),row['path']
        data=p.read_bytes();assert len(data)==row['bytes'] and c.sha(data)==row['sha256'],row['path'];total+=len(data)
    for name in ['source_calibration_lock.json','extraction_lock.json','fragment_library_lock.json']:
        for rel,digest in c.load(root/name)['files'].items():assert c.sha((root/rel).read_bytes())==digest,(name,rel)
    print(json.dumps({'verified':True,'root':str(root),'artifacts':len(m['artifacts']),'bytes':total,'LLM_requests':0,'GP_attempts':0},ensure_ascii=False),flush=True)

def audit_archives():
    manifests=c.load(ROOT/'source_archive_lock.json');rows=[]
    for name in ARCHIVES:
        folder=ROOT.parent/name;mp=folder/'manifest.json';assert c.sha(mp.read_bytes())==manifests[name],name
        count=0;size=0
        for row in c.load(mp)['artifacts']:
            p=(folder/row['path']).resolve();assert p.is_relative_to(folder.resolve())
            data=p.read_bytes();assert len(data)==row['bytes'] and c.sha(data)==row['sha256'],str(p)
            count+=1;size+=len(data)
        rows.append({'archive':name,'manifest_sha256':manifests[name],'verified_files':count,'verified_bytes':size,'unchanged':True})
        print('Archive unchanged:',name,count,flush=True)
    save(ROOT/'archive_integrity_audit.json',{'checked_at':c.now(),'all_unchanged':True,'archives':rows,'verified_files':sum(r['verified_files'] for r in rows)})

def final():
    assert not (ROOT/'fragment_library_lock.json').exists(),'Frozen libraries: use verify instead of rewriting'
    check_lock('source_calibration_lock.json');check_lock('extraction_lock.json')
    assert c.load(ROOT/'extraction/evaluation_complete.json')['evaluated_programs']==1166
    gate=c.load(ROOT/'extraction/calibration_gate.json');assert gate['passed']
    repository_source=ROOT.parent/'baseline_calibration_01/sources/repository_version.json'
    shutil.copy2(repository_source,ROOT/'sources/repository_version.json')
    save(ROOT/'sources/reference_provenance.json',{'repository_version_source':str(repository_source),
        'repository_version_sha256':c.sha(repository_source.read_bytes()),
        'reference_rules':{name:{'path':f'rules/{name}.py','sha256':c.sha((ROOT/'rules'/f'{name}.py').read_bytes())}
                           for name in ['Best-fit','EoH','Historical-best']}})
    programs=c.load(ROOT/'sources/program_registry.json');selected=c.load(ROOT/'sources/selected_1242.json')
    assert len(programs)==len(selected)==1242
    original_ids={r['candidate_id'] for r in csv.DictReader((ROOT.parent/'behavior_stage1_01/candidate_quality.csv').open(encoding='utf-8-sig'))}
    assert {r['candidate_id'] for r in selected}==original_ids and len(original_ids)==1242
    assert {r['program_id'] for r in programs}==original_ids
    assert c.sha((ROOT/'sources/stage1_registry.json').read_bytes())==c.sha((ROOT.parent/'behavior_stage1_01/candidates_registry.json').read_bytes())
    selection_by_id={r['candidate_id']:r for r in selected}
    origin_by_id={r['candidate_id']:r for r in c.load(ROOT/'sources/stage1_registry.json')}
    by_id={r['program_id']:r for r in programs};accepted={};excluded=[];instance_rows=[];groups=collections.defaultdict(list)
    total_pack=total_probe=matched_exceptions=nonfinite_probes=0
    for row in programs:
        assert c.sha((ROOT/row['code_path']).read_bytes())==row['code_sha256']
        assert row['origins']==origin_by_id[row['program_id']]['origins']
        assert row['code_sha256']==selection_by_id[row['program_id']]['source_file_sha256']
        assert c.sha((ROOT/row['code_path']).read_text(encoding='utf-8'))==selection_by_id[row['program_id']]['registry_code_sha256']
        if not row['convertible']:
            excluded.append({'program_id':row['program_id'],'phase':'static conversion','reason':row['error']});continue
        result=c.load(ROOT/'extraction/results'/f"{row['program_id']}.json")
        assert result['program_id']==row['program_id']
        if not result['valid']:
            excluded.append({'program_id':row['program_id'],'phase':'equivalence/full packing','reason':result['error']});continue
        assert result['probe_score_comparisons']==64 and len(result['instances'])==5
        assert result['resource_limit']['enforced'] and result['resource_limit']['bytes']==536870912
        signature=[]
        with np.load(ROOT/result['trace_path'],allow_pickle=False) as traces:
            for item in result['instances']:
                assert item['original_bins']==item['expanded_bins']==item['normalized_bins']
                indices=traces['indices_'+item['instance_id']];caps=traces['capacities_'+item['instance_id']]
                assert indices.shape==caps.shape==(5000,)
                assert c.sha(np.asarray(indices,dtype='<i4').tobytes())==item['trace_hash']
                assert c.sha(np.asarray(caps,dtype='<i2').tobytes())==item['capacity_hash']
                signature.append([item['instance_id'],item['trace_hash'],item['capacity_hash']])
                instance_rows.append({'dataset':'pilot_dev','program_id':row['program_id'],**item,'error':''})
        assert result['mean_bins']==float(np.mean([x['original_bins'] for x in result['instances']]))
        groups[c.sha(json.dumps(signature,separators=(',',':')))].append(row['program_id'])
        accepted[row['program_id']]=result
        total_pack+=result['packing_state_score_comparisons'];total_probe+=result['probe_score_comparisons']
        matched_exceptions+=result.get('matched_probe_exceptions',0);nonfinite_probes+=result['nonfinite_probe_outputs']
    mismatches=[r for r in excluded if 'Mismatch' in r['reason']]
    assert not mismatches,'Conversion mismatch requires investigation before freezing'
    raw_path=ROOT/'extraction/raw_fragments.json';clean_path=ROOT/'extraction/clean_fragments.json'
    raw=c.load(raw_path);clean=c.load(clean_path)
    pre_hashes={'raw_fragments':c.sha(raw_path.read_bytes()),'clean_fragments':c.sha(clean_path.read_bytes())}
    raw_map={r['key']:r for r in raw};clean_map={r['key']:r for r in clean}
    assert len(raw_map)==len(raw) and len(clean_map)==len(clean)
    expected_raw=collections.defaultdict(list);expected_clean=collections.defaultdict(list)
    # Rebuild directly from original source, preserving original AST source locations.
    # This corrects catalog's serialized-expression line=1 metadata, not expression contents.
    for i,(pid,result) in enumerate(accepted.items(),1):
        row=by_id[pid];expanded,deps=t.expand_program((ROOT/row['code_path']).read_text(encoding='utf-8'))
        assert t.text(expanded)==row['expression'] and deps==row['dependencies']
        (ROOT/'converted_programs').mkdir(exist_ok=True)
        for label,node in [('expanded',expanded),('normalized',t.canonical(expanded))]:
            # np import provides exactly the module dependency recorded in the libraries.
            (ROOT/'converted_programs'/f'{pid}_{label}.py').write_text('import numpy as np\n\n'+t.program(node),encoding='utf-8')
        save(ROOT/'extraction/expression_trees'/f'{pid}.json',{'program_id':pid,'source_code_path':row['code_path'],
            'expanded_expression':row['expression'],'expanded_tree':tree_payload(expanded),
            'normalized_expression':row['normalized_expression'],'normalized_tree':tree_payload(t.canonical(expanded))})
        for path,node,kind in t.locations(expanded):
            k=t.key(node);normal=t.canonical(node);nk=t.key(normal)
            src={'program_id':pid,'expanded_path':[list(part) for part in path],
                 'source_line':node.lineno,'origin_multiplicity':max(1,len(row['origins']))}
            expected_raw[k].append(src);expected_clean[nk].append(src)
            assert raw_map[k]['type']==kind and clean_map[nk]['type']==t.infer(normal)
            assert k in clean_map[nk]['raw_keys']
        if i%200==0:print('Library provenance audited',i,'/',len(accepted),flush=True)
    assert set(expected_raw)==set(raw_map) and set(expected_clean)==set(clean_map)
    def sig(src):return (src['program_id'],json.dumps(src['expanded_path']),src['origin_multiplicity'])
    for lib,expected,normalized in [(raw,expected_raw,False),(clean,expected_clean,True)]:
        for fragment in lib:
            k=fragment['key'];want=expected[k]
            assert collections.Counter(map(sig,fragment['sources']))==collections.Counter(map(sig,want))
            lines={sig(s):s['source_line'] for s in want}
            for source in fragment['sources']:
                source['serialized_expression_line']=source.pop('source_line')
                source['source_line']=lines[sig(source)]
            node=t.parse(fragment['expression']);node=t.canonical(node) if normalized else node
            assert t.key(node)==k and t.infer(node)==fragment['type']
            assert t.size(node)==fragment['size'] and t.depth(node)==fragment['depth']
            names={n.id for n in ast.walk(node) if isinstance(n,ast.Name)}
            assert names<={'item','bins','np','abs','min','max','float','int','len','round'},(k,names)
            assert fragment['terminal_dependencies']==sorted(names&{'item','bins'})
            assert fragment['module_dependencies']==(['numpy as np'] if 'np' in names else [])
            if not normalized:assert fragment['occurrence_weight']==sum(s['origin_multiplicity'] for s in want)
    save(raw_path,raw);save(clean_path,clean)
    save(ROOT/'extraction/provenance_audit.json',{'passed':True,'checked_at':c.now(),'catalog_before_provenance_sha256':pre_hashes,
        'metadata_correction':'source_line now points to original source AST; prior line retained as serialized_expression_line. No expression/key/type/source membership changed.',
        'all_sources_and_occurrences_reconstructed':True,'all_fragments_self_contained_and_typed':True,'no_behavior_or_quality_pruning':True})
    table('extraction/conversion_instance_results.csv',instance_rows)
    table('extraction/excluded_programs.csv',excluded)
    table('extraction/fragment_index.csv',[
        {'library':name,'key':r['key'],'type':r['type'],'nodes':r['size'],'depth':r['depth'],'source_occurrences':len(r['sources']),
         'terminal_dependencies':','.join(r['terminal_dependencies']),'expression':r['expression']}
        for name,lib in [('raw',raw),('clean',clean)] for r in lib])
    save(ROOT/'extraction/full_pilot_dev_behavior_groups.json',{'scope':'observed complete choices/capacities on five pilot_dev only; NOT universal semantic equivalence; NOT used for deduplication',
        'groups':[{'signature_sha256':key,'program_ids':ids,'program_count':len(ids)} for key,ids in sorted(groups.items())]})
    save(ROOT/'extraction/library_schema.json',{'format_version':1,'frozen':True,
        'source_programs':1242,'inputs':{'item':'numeric scalar','bins':'read-only 1D feasible-bin remaining capacities'},
        'types':{'S':'numeric scalar (including NumPy 0D)','V':'numeric vector with len(bins)','BS':'boolean scalar','BV':'boolean vector with len(bins)'},
        'np_dependency':'import numpy as np; builtin callable dependencies explicitly supported by typed_tree.infer',
        'key':'sha256(ast.dump(expression, include_attributes=False)); normalized negative literals must canonicalize after parse before key computation',
        'source_line':'original source AST line for this expanded subtree root; local expansion may duplicate source nodes',
        'serialized_expression_line':'line when catalog reparsed single expression; not an original source line',
        'expanded_path':'ordered (AST field, list index or null) components from complete score root',
        'raw_storage':'one record per exact structural key; every source occurrence and origin multiplicity retained',
        'clean_storage':'type-checked normalization and certain structural key merge only',
        'normalization':'local dependencies inlined to item/bins; numeric unary plus, literal unary sign, double negation only',
        'no_deletion_on':'quality, Worst-fit, constant/order-invariant, finite-probe behavior, future GP size limits',
        'frozen_libraries':'Search may sample only these libraries; never append based on search outputs.'})
    summary=c.load(ROOT/'extraction/summary.json');assert summary['verified_full_packing_programs']==len(accepted)
    summary.update(original_source_provenance_verified=True,full_pilot_dev_observed_behavior_groups=len(groups),
        total_original_packing_state_score_comparisons=total_pack,total_fixed_probe_comparisons=total_probe,
        matched_probe_exceptions=matched_exceptions,nonfinite_probe_outputs=nonfinite_probes,
        raw_unweighted_source_occurrences=sum(len(r['sources']) for r in raw),
        maximum_raw_fragment_nodes=max(r['size'] for r in raw),maximum_raw_fragment_depth=max(r['depth'] for r in raw))
    save(ROOT/'extraction/summary.json',summary)
    if not (ROOT/'archive_integrity_audit.json').exists():audit_archives()
    prior_audit=c.load(ROOT/'archive_integrity_audit.json');assert prior_audit['all_unchanged']
    assert {r['archive'] for r in prior_audit['archives']}==set(ARCHIVES)
    for record in prior_audit['archives']:
        assert c.sha((ROOT.parent/record['archive']/'manifest.json').read_bytes())==record['manifest_sha256']
    exclusions=collections.Counter(r['reason'] for r in excluded)
    quality=[r['mean_bins'] for r in accepted.values()]
    rawtypes=collections.Counter(r['type'] for r in raw);cleantypes=collections.Counter(r['type'] for r in clean)
    elapsed=c.load(ROOT/'extraction/evaluation_complete.json')['this_session_wall_seconds']
    report=['# 歷史程式轉換與兩個固定片段庫', '',
        '已完成本次三步。新 LLM 請求 **0**、GP／演化候選嘗試 **0**。僅使用既有 1,242 個有效歷史程式與原 pilot_dev；未評估 pilot_val。', '',
        '## 1．資料與參考重現', '',
        'pilot_dev 沿用五個 6001–6005 實例，容量 100、每例 5,000 物品。資料逐位元保持原樣；物品不排序，只向已開啟且可容納的箱子評分，取最高分，平手選第一個可容納箱，沒有可容納箱才開箱。', '',
        '| 程式 | 平均箱數 | 相對 Best-fit 少用箱數 | 重現 |',
        '| --- | ---: | ---: | --- |']
    for r in gate['results']:report.append(f"| {r['heuristic']} | {r['mean_bins']:.1f} | {2066.4-r['mean_bins']:.1f} | 五例箱數及完整選箱／容量軌跡一致 |")
    report += ['', '資料是既有 WB3S45_INT_C100_N5000_v1（floor、clip）pilot 資料，不是官方原始五例的 round 資料。pilot_val 原樣保留，已被查看，只供未來小實驗診斷。', '',
        f"公開 EoH 使用已校準的原始程式，未經轉換器；保存來源版本 {c.load(repository_source)['commit']}、論文版本 {c.load(repository_source)['paper_version']} 與規則 SHA256，詳見 sources/reference_provenance.json 及 repository_version.json。", '',
        '## 2．轉換覆蓋率與完整等價核對', '',
        '| 項目 | 數量 |','| --- | ---: |',f'| 既有有效來源（無品質篩選） | 1,242 |',
        f"| 靜態可轉換 | {summary['static_convertible_programs']:,} |",f'| 完整驗證通過並提供片段 | {len(accepted):,}（{len(accepted)/1242:.2%}） |',
        f'| 排除並保存原因 | {len(excluded):,} |',f'| 固定合法探針比較 | {total_probe:,} |',
        f'| 原始完整装箱軌跡評分狀態比較 | {total_pack:,} |',f'| 轉換造成分數／決策不一致 | {len(mismatches)} |', '',
        '按語句順序展開局部變數，保存直接依賴、原始行號、展開式及型別。第一版只接受明確的純量、同長度數值向量與布林遮罩運算；不支援的型別混用、動態形狀／索引等保留排除紀錄，沒有修復或改寫歷史程式。', '',
        '每個可轉換程式先比原始、展開、規範化三版本的 64 個合法狀態分數：shape、dtype 與值完全相同（equal_nan）。再核對原始五例完整軌跡每次評分；三版本各自完整装箱，箱數、每一步選箱索引與所選容量一致。驗證只涵蓋已列探針與 pilot_dev，不能由有限資料宣稱所有輸入上的形式化等價。', '',
        f'探針三版本相同例外 {matched_exceptions:,} 次、相同非有限分數 {nonfinite_probes:,} 次，僅記錄；實際完整裝箱仍要求有限且合法的分數。', '',
        '排除原因（詳見 excluded_programs.csv；同一程式只記第一個阻礙）：', '', '| 原因 | 程式數 |','| --- | ---: |']
    report += [f'| {reason.replace("|","/")} | {count} |' for reason,count in exclusions.most_common()]
    report += ['', '## 3．固定片段庫', '', '| 項目 | 數量 |','| --- | ---: |',
        f"| 原始庫：確定結構唯一片段 | {len(raw):,} |",f"| 原始子樹出現次數（未加來源權重） | {summary['raw_unweighted_source_occurrences']:,} |",
        f"| 原始出現次數（歷史出處 multiplicity 加權） | {summary['raw_fragment_occurrences_weighted']:,} |",
        f'| 整理庫：規範化後結構唯一片段 | {len(clean):,} |',f"| 多個原始結構合併的規範化群 | {summary['normalization_merging_groups']:,} |", '',
        '| 型別 | 原始庫 | 整理庫 |','| --- | ---: | ---: |']
    report += [f'| {kind} | {rawtypes[kind]:,} | {cleantypes[kind]:,} |' for kind in ['S','V','BS','BV']]
    report += ['',
        '原始庫只將完全相同 AST 結構共用一份記錄，保留每次出現的來源與權重。整理庫做型別檢查、完整展開局部變數至標準 item/bins、保守 unary 符號規範化，再去除確定結構重複。不重排浮點運算，也不因 Worst-fit、常數、單獨不改排序或有限狀態上的相同行為刪除任何子樹。', '',
        '每片段均已重新解析並檢查型別，terminal 輸入依賴只有 item/bins；NumPy／合法內建函式依賴另記。sources 記錄來源程式 ID、展開樹路徑、原始行號；完整 local 依賴在 program_registry.json。來源行號是從原始 AST 重新重建；單行序列化後的行號另外保存，避免當成原始出處。', '',
        f"最大原始片段 {summary['maximum_raw_fragment_nodes']:,} 節點、{summary['maximum_raw_fragment_depth']} 層。本次未套用未來 GP 的大小限制。", '',
        f'完整 pilot_dev 決策軌跡有 {len(groups):,} 個觀察群，僅作診斷，不據此去重；它們也不等於所有輸入上的語意等價。通過來源在 pilot_dev 的平均箱數範圍 {min(quality):.1f}–{max(quality):.1f}，僅為歷史來源描述，不是新搜尋成果。', '',
        '## CPU 成本與封存', '',
        f"完整驗證本次牆鐘 {elapsed:.1f} 秒；各隔離程序牆鐘合計 {summary['worker_wall_seconds_sum']:.1f} 秒。至多四程序、每程序 512 MiB／120 秒、BLAS 單執行緒。程序合計不可當成使用者等待時間。", '',
        f"單一展開程式完整跑五例的實測時間中位數 {summary['five_instance_expanded_runtime_median']:.3f} 秒、P95 {summary['five_instance_expanded_runtime_p95']:.3f} 秒；並行執行下量測，供後續預算評估，並未啟動搜尋。", '',
        'fragment_library_lock.json 鎖定兩庫、來源、依賴、驗證結果、資料及實作雜湊。後續搜尋只讀固定庫，不隨搜尋成果追加材料。manifest.json 可驗證整份交付；十個既有封存 manifest 與其中每個檔案已逐檔檢查不變。', '',
        '主要交付：extraction/raw_fragments.json、extraction/clean_fragments.json、sources/program_registry.json、extraction/expression_trees/、converted_programs/、extraction/program_coverage.csv、extraction/conversion_instance_results.csv、traces/、extraction/library_schema.json、archive_integrity_audit.json。', '',
        '重現入口見 README.md；已固定的工作目錄請只執行 verify，若要重新評估應使用獨立副本，避免覆寫封存庫。', '']
    (ROOT/'REPORT.md').write_text('\n'.join(report),encoding='utf-8')
    save(ROOT/'audit_checks.json',{'passed':True,'checked_at':c.now(),'all_and_only_1242_sources':True,
        'unchanged_pilot_data':True,'three_references_reproduced':True,'accepted_source_exact_scores_and_full_packing':True,
        'all_trace_files_rehashed':True,'all_subtrees_reconstructed':True,'independent_typed_fragments':True,
        'original_source_lines_verified':True,'structural_dedup_only':True,'historical_archives_unchanged':True,
        'pilot_val_not_evaluated':True,'LLM_requests':0,'GP_attempts':0})
    files=[p for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and not p.name.endswith('.tmp') and p.name not in {'manifest.json','fragment_library_lock.json'}]
    save(ROOT/'fragment_library_lock.json',{'frozen_at':c.now(),'LLM_requests':0,'GP_attempts':0,
        'no_appending_from_search':True,'raw_fragments':len(raw),'clean_fragments':len(clean),
        'files':{p.relative_to(ROOT).as_posix():c.sha(p.read_bytes()) for p in sorted(files)}})
    files.append(ROOT/'fragment_library_lock.json')
    artifacts=[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':c.sha(p.read_bytes())} for p in sorted(files)]
    save(ROOT/'manifest.json',{'experiment':'fragment_gp_01','scope':'only three preparatory steps','LLM_requests':0,'GP_attempts':0,'artifacts':artifacts})
    verify(ROOT)

if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='verify':verify(sys.argv[2] if len(sys.argv)>2 else ROOT)
    else:final()
