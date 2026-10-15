"""Read-only provenance replay of the frozen 30 search seeds; no packing/search."""
import ast,collections,csv,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent
SOURCE=BASE/'fragment_gp_limited_30seed_extension_01'
sys.path.insert(0,str(SOURCE))
import typed_tree as t
import gp_search as g
def sha(b):return hashlib.sha256(b).hexdigest()
def save(name,x):(ROOT/name).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def table(name,rows):
    with (ROOT/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
archives=[BASE/'fragment_gp_limited_01',BASE/'fragment_gp_limited_20seed_extension_01',SOURCE]
manifests={p:{r['path']:r for r in json.loads((p/'manifest.json').read_text(encoding='utf-8'))['artifacts']} for p in archives}
used={}
def read(p):
    p=Path(p);data=p.read_bytes();archive=next(a for a in archives if p.is_relative_to(a));rel=p.relative_to(archive).as_posix()
    r=manifests[archive][rel];assert len(data)==r['bytes'] and sha(data)==r['sha256'],str(p)
    used[str(p)]={'bytes':len(data),'sha256':sha(data)};return data.decode('utf-8-sig')
def load(p):return json.loads(read(p))
def csvread(p):return list(csv.DictReader(read(p).splitlines()))
def paths(node):return {p for p,_,_ in t.locations(node)}
def transplanted(tags,target,donor_tags,donor_path=()):
    out={p:v for p,v in tags.items() if p[:len(target)]!=target}
    out.update({target+p[len(donor_path):]:v for p,v in donor_tags.items() if p[:len(donor_path)]==donor_path})
    return out
raw={r['key']:r for r in load(SOURCE/'libraries/raw_fragments.json')}
events={};focus_rows=[];run_rows=[];ancestry_rows=[];fragment_usage=collections.Counter();inputs_by_run=[]
for archive in archives:
    init=load(archive/'initialization/results.json');summaries=csvread(archive/'run_summary.csv')
    attempts=csvread(archive/'attempt_results.csv');parent_rows=csvread(archive/'parent_reproduction.csv')
    for summary in summaries:
        method=summary['method'];seed=int(summary['seed']);label=f'{method}_{seed}'
        state=load(archive/'runs'/label/'checkpoint.json');done=load(archive/'runs'/label/'complete.json')
        logs=state['log'];assert len(logs)==112 and state['completed']==112
        csvlogs=[r for r in attempts if r['method']==method and int(r['seed'])==seed]
        assert len(csvlogs)==112
        receiver=collections.Counter(l['parent_id'] for l in logs)
        donor=collections.Counter(l['second_parent_id'] for l in logs if l['second_parent_id'])
        prs=[r for r in parent_rows if r['method']==method and int(r['seed'])==seed]
        for r in prs:
            assert int(r['receiver_events'])==receiver[r['parent_id']] and int(r['donor_events'])==donor[r['parent_id']]
        assert {r['parent_id'] for r in prs}==set(receiver)|set(donor)
        nodes={r['id']:r for r in init[str(seed)]};tags={i:{p:frozenset() for p in paths(g.dec(r['tree']))} for i,r in nodes.items()}
        ancestors={i:set() for i in nodes};insertions={i:set() for i in nodes};primary={i:[] for i in nodes}
        by_id={l['candidate_id']:l for l in logs}
        for log,cl in zip(logs,csvlogs):
            cid=log['candidate_id'];p=load(archive/'candidates'/f'{cid}.json')
            for field in ['parent_id','second_parent_id','operator','fragment_key','replacement_source']:
                assert p[field]==log[field] and ('' if log[field] is None else str(log[field]))==cl[field]
            assert int(cl['attempt'])==log['attempt'] and cl['valid']==str(log['valid'])
            parent=p['parent_id'];second=p['second_parent_id'];target=tuple(tuple(c) for c in p['target_path'])
            a=set(ancestors[parent]);a.add(parent);ins=set(insertions[parent]);newtags=dict(tags[parent])
            if not p['construction_error']:
                if p['operator']=='crossover':
                    donor_path=tuple(tuple(c) for c in p['donor_path']);newtags=transplanted(newtags,target,tags[second],donor_path)
                    a.update(ancestors[second]);a.add(second);ins.update(insertions[second])
                elif p['operator']=='subtree_replace':
                    if p['replacement_source']=='historical_fragment':
                        key=p['fragment_key'];frag=t.parse(raw[key]['expression']);events[cid]={'event_id':cid,'fragment_key':key,'expression':raw[key]['expression'],'source_program_ids':sorted({x['program_id'] for x in raw[key]['sources']})}
                        donor_tags={q:frozenset([cid]) for q in paths(frag)};ins.add(cid);fragment_usage[(method,key)]+=1
                    else:
                        # Replay basic donor using the original per-attempt random channel.
                        rr=g.rng(seed,p['attempt'],6);frag=t.random_tree(p['target_type'],rr,levels=int(rr.integers(1,4)),safe=True)
                        donor_tags={q:frozenset() for q in paths(frag)}
                    newtags=transplanted(newtags,target,donor_tags)
                else:newtags=transplanted(newtags,target,{():frozenset()})
            tree=g.dec(p['tree']);assert set(newtags)==paths(tree),(label,cid)
            tags[cid]=newtags;ancestors[cid]=a;insertions[cid]=ins;primary[cid]=primary[parent]+[parent];nodes[cid]=p
        first_parent=next((l['candidate_id'] for l in logs if l['improves_parent']),None)
        first_initial=next((l['candidate_id'] for l in logs if l['improves_initial_best']),None)
        fq=float(summary['final_dev']);initial=float(summary['initial_best_dev'])
        first_final=state['initial_best']['id'] if fq==initial else next(l['candidate_id'] for l in logs if l['valid'] and l['mean_bins']==fq)
        final=done['best']['id'];assert final==summary['final_id']
        improved=fq<initial;target_rows={}
        for role,cid in [('first_parent_improvement',first_parent),('first_initial_improvement',first_initial),('first_final_quality',first_final),('selected_final',final)]:
            if cid is None:continue
            p=nodes[cid];anc=ancestors[cid];inserts=insertions[cid];surv=set().union(*tags[cid].values()) if tags[cid] else set()
            intact=set()
            for path,node,_ in t.locations(g.dec(p['tree'])):
                for event in tags[cid][path]:
                    if t.key(node)==events[event]['fragment_key']:intact.add(event)
            ancestor_children=sorted((x for x in anc if x in by_id),key=lambda x:by_id[x]['attempt'])
            ops=collections.Counter(by_id[x]['operator'] for x in ancestor_children)
            lineage_keys=sorted({events[x]['fragment_key'] for x in inserts});surv_keys=sorted({events[x]['fragment_key'] for x in surv})
            row={'method':method,'seed':seed,'run_improved_initial':improved,'role':role,'candidate_id':cid,'attempt':p.get('attempt',0),
                 'mean_bins':by_id[cid]['mean_bins'] if cid in by_id else p['mean_bins'],'nodes':p['nodes'],'depth':p['depth'],
                 'operation':p.get('operator','initialization'),'parent_id':p.get('parent_id',''),'second_parent_id':p.get('second_parent_id',''),
                 'receiver_was_previous_child':bool(p.get('parent_id') in by_id),'donor_was_previous_child':bool(p.get('second_parent_id') in by_id),
                 'ancestor_child_operations':len(ancestor_children),'ancestor_crossover':ops['crossover'],'ancestor_subtree_replace':ops['subtree_replace'],'ancestor_constant_mutation':ops['constant_mutation'],
                 'ancestral_insert_events':len(inserts),'ancestral_distinct_fragment_keys':len(lineage_keys),'surviving_insert_events':len(surv),'surviving_distinct_fragment_keys':len(surv_keys),
                 'intact_insert_events':len(intact),'fragment_tagged_internal_nodes':sum(bool(v) for v in tags[cid].values()),
                 'primary_chain_child_parent_count':sum(x in by_id for x in primary[cid]),'ancestral_fragment_keys':json.dumps(lineage_keys),'surviving_fragment_keys':json.dumps(surv_keys),
                 'ancestral_event_ids':json.dumps(sorted(inserts)),'surviving_event_ids':json.dumps(sorted(surv)),'intact_event_ids':json.dumps(sorted(intact))}
            focus_rows.append(row);target_rows[role]=row
            for x in ancestor_children+([cid] if cid in by_id else []):
                q=nodes[x];log=by_id[x]
                ancestry_rows.append({'method':method,'seed':seed,'role':role,'target_candidate':cid,'ancestor_candidate':x,'attempt':q['attempt'],'operator':q['operator'],'parent_id':q['parent_id'],'second_parent_id':q['second_parent_id'],'fragment_key':q['fragment_key'],'replacement_source':q['replacement_source'],'valid':log['valid'],'mean_bins':log['mean_bins'],'improves_initial':log['improves_initial_best'],'expression':q['expression']})
        fr=target_rows['selected_final']
        run_rows.append({'method':method,'seed':seed,'improved_initial':improved,'initial_bins':initial,'final_bins':fq,'gain':initial-fq,
                         'first_initial_improvement_attempt':by_id[first_initial]['attempt'] if first_initial else None,'first_final_quality_attempt':nodes[first_final].get('attempt',0),'selected_final_attempt':nodes[final].get('attempt',0),
                         'historical_insert_attempts':sum(l['replacement_source']=='historical_fragment' for l in logs),'successful_construction_inserts':sum(nodes[l['candidate_id']]['replacement_source']=='historical_fragment' and not nodes[l['candidate_id']]['construction_error'] for l in logs),
                         'receiver_child_events':sum(l['parent_id'] in by_id for l in logs),'donor_child_events':sum(l['second_parent_id'] in by_id for l in logs),
                         'final_ancestral_inserts':fr['ancestral_insert_events'],'final_surviving_inserts':fr['surviving_insert_events'],'final_intact_inserts':fr['intact_insert_events'],
                         'final_ancestral_operations':fr['ancestor_child_operations'],'final_receiver_was_child':fr['receiver_was_previous_child'],'final_donor_was_child':fr['donor_was_previous_child']})
groups=[]
for method in g.METHODS:
    for status in [True,False]:
        rows=[r for r in run_rows if r['method']==method and r['improved_initial']==status]
        if not rows:continue
        mean=lambda k:sum(r[k] for r in rows)/len(rows)
        groups.append({'method':method,'improved_initial':status,'runs':len(rows),'mean_gain':mean('gain'),'mean_receiver_child_events':mean('receiver_child_events'),
                       'mean_insert_attempts':mean('historical_insert_attempts'),'mean_final_ancestral_inserts':mean('final_ancestral_inserts'),
                       'final_with_multiple_ancestral_inserts':sum(r['final_ancestral_inserts']>=2 for r in rows),'final_with_multiple_surviving_inserts':sum(r['final_surviving_inserts']>=2 for r in rows),'final_with_multiple_intact_inserts':sum(r['final_intact_inserts']>=2 for r in rows)})
assert len(run_rows)==90 and len({r['seed'] for r in run_rows})==30
table('run_mechanisms.csv',run_rows);table('focus_candidate_provenance.csv',focus_rows);table('ancestor_operations.csv',ancestry_rows);table('improved_vs_unimproved.csv',groups)
save('fragment_insert_events.json',events)
usage=[]
for (method,key),count in fragment_usage.most_common():
    rr=raw[key];usage.append({'method':method,'key':key,'insertions':count,'type':rr['type'],'expression':rr['expression'],'source_program_ids':json.dumps(sorted({x['program_id'] for x in rr['sources']}))})
table('fragment_usage.csv',usage)
lines=['# 30種子封存搜尋：候選來源與祖先鏈診斷','',
       '資料限定原三種子、追加17與追加10，共30種子／90run。本步零新候選、零完整裝箱評估、零LLM。所有讀取的attempt_results.csv、parent_reproduction.csv、checkpoint、候選及初始化均核对原核心封存雜湊。','',
       '首次改善定義為子代的完整pilot_dev平均箱數嚴格小於初始最佳；另存首次改善父代、首次達到最終品質與最後被選中的候選。最後一者可能在同品質下經過節點數／鍵值淘汰，不必與首次達到該品質同一支。','',
       '祖先事件統計合併接收父代與交叉供體的DAG；建立失敗沿用接收父代的樹。片段來源標籤按內部AST節點傳遞、替換時移除被覆蓋部分；「仍有來源節點」不表示整片段未改動。完整保留另以相同AST子樹判斷。以上只是來源證據，不是收益歸因或因果消融。','',
       '| 方法 | run改善 | run數 | 平均改善 | 子代作接收父代次數 | 最終祖先插入均數 | 最終≥2祖先插入 | 最終≥2來源插入仍存節點 | 最終≥2完整片段 |','|---|---|---:|---:|---:|---:|---:|---:|---:|']
for r in groups:lines.append(f"| {r['method']} | {r['improved_initial']} | {r['runs']} | {r['mean_gain']:.3f} | {r['mean_receiver_child_events']:.2f} | {r['mean_final_ancestral_inserts']:.2f} | {r['final_with_multiple_ancestral_inserts']} | {r['final_with_multiple_surviving_inserts']} | {r['final_with_multiple_intact_inserts']} |")
lines+=['','## 原始片段GP各種子','',
        '| seed | 改善 | 首次改善 | 首達最終品質 | 最終選中嘗試 | 祖先插入／仍存／完整 | 最終接收父代為子代 |','|---|---:|---:|---:|---:|---|---|']
for r in run_rows:
    if r['method']=='raw_fragment_gp':lines.append(f"| {r['seed']} | {r['gain']:.1f} | {r['first_initial_improvement_attempt']} | {r['first_final_quality_attempt']} | {r['selected_final_attempt']} | {r['final_ancestral_inserts']}/{r['final_surviving_inserts']}/{r['final_intact_inserts']} | {r['final_receiver_was_child']} |")
lines+=['','逐項來源：focus_candidate_provenance.csv列每個目標的片段鍵与事件；fragment_insert_events.json／fragment_usage.csv列原式與歷史來源ID；ancestor_operations.csv保存目標祖先各步的兩個父代、操作與完整式。run_mechanisms.csv與improved_vs_unimproved.csv涵蓋全部run，不能只挑成功例。','',
        '值得後續驗證的機制應以這些結果提出；多次插入可能只是更長祖先鏈、更多搜尋機會或成功後保留的結果。匹配隨機片段GP可比較歷史內容先驗與同等大小型別庫的作用，仍非個別片段組合的因果證明。','']
(ROOT/'REPORT.md').write_text('\n'.join(lines),encoding='utf-8')
save('input_integrity.json',{'passed':True,'source_archives':[{ 'path':str(p),'manifest_sha256':sha((p/'manifest.json').read_bytes())} for p in archives],'files':used,'runs':90,'search_seeds':30,'new_search_attempts':0,'new_full_packing_evaluations':0,'LLM_requests':0,'node_provenance_replayed':True,'parent_reproduction_csv_counts_verified':True})
save('manifest.json',{'files':{p.name:sha(p.read_bytes()) for p in ROOT.iterdir() if p.is_file() and p.name!='manifest.json'}})
print(json.dumps(groups,ensure_ascii=False),flush=True)
