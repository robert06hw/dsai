"""Read-only experiment-plan integrity checks. Never executes scoring or GP."""
import collections,csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    lock=load(ROOT/'registration_lock.json')
    for name,h in lock['files'].items():assert sha(ROOT/name)==h,name
    for rel,meta in load(ROOT/'source_manifest.json')['workspace_relative_paths'].items():
        p=ROOT.parent/rel;assert sha(p)==meta['sha256'] and p.stat().st_size==meta['bytes'],rel
    cfg=load(ROOT/'config.json');test=load(ROOT/'test_data_plan.json')
    with (ROOT/'run_schedule.csv').open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
    assert len(rows)==cfg['runs']==30 and sum(int(r['wall_seconds']) for r in rows)==3600
    assert sorted(int(r['run_order']) for r in rows)==list(range(1,31))
    for seed in cfg['search_seeds']:
        rs=[r for r in rows if int(r['search_seed'])==seed]
        assert len(rs)==3 and {r['method'] for r in rs}==set(cfg['methods'])
    balance={m:dict(collections.Counter(int(r['within_block_order']) for r in rows if r['method']==m)) for m in cfg['methods']}
    assert all(max(v.values())-min(v.values())<=1 for v in balance.values())
    plans=load(ROOT/'initialization_plans.json')
    assert set(plans)==set(map(str,cfg['search_seeds']))
    assert all(len(v)==16 and v[0]['source']=='Best-fit' and all(r['nodes']<=64 and r['depth']<=8 and r['type']=='V' for r in v) for v in plans.values())
    seeds=cfg['search_seeds']+test['seeds']+test['duplicate_only_backup_seeds']
    assert len(seeds)==len(set(seeds))==70
    old=load(ROOT/'seed_selection_audit.json')['previous_seed_values'];assert not set(old)&set(seeds)
    states=load(ROOT/'frozen/states.json');assert collections.Counter(r['set'] for r in states)=={'A':64,'B':64}
    assert cfg['executed_search_runs']==cfg['executed_full_evaluations']==cfg['new_LLM_requests']==0
    assert not any((ROOT/p).exists() for p in ['runs','evaluations','final_candidates','test_data'])
    result={'passed':True,'locked_files_verified':len(lock['files']),'source_files_verified':len(load(ROOT/'source_manifest.json')['workspace_relative_paths']),
        'paired_runs':30,'paired_seeds':10,'nominal_search_seconds':3600,'order_position_counts':balance,'initial_slots_planned':160,
        'frozen_A_states':64,'models_byte_identical':True,'test_content_nonoverlap':'pending generation; not claimed checked',
        'runner_implementation':'not yet implemented; execution lock required','search_started':False,'full_evaluations':0,'new_LLM_requests':0,
        'registration_lock_sha256':sha(ROOT/'registration_lock.json')}
    (ROOT/'registration_audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
