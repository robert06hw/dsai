"""Hash, structure and deterministic search audits; no new search or LLM calls."""
import ast,collections,json,time
from pathlib import Path
from .runtime import ROOT,ASSETS,configure,load,sha,save
from .analysis import csvrows
def verify_files():
 expected=load(ROOT/'REPRODUCIBILITY_MANIFEST.json')['files'];bad=[]
 for rel,record in expected.items():
  path=ROOT/rel
  if not path.is_file() or sha(path)!=record['sha256']:bad.append(rel)
 if bad:raise ValueError('Changed or missing packaged files: '+', '.join(bad[:10]))
 config=load(ROOT/'configs/study.json');programs=load(ASSETS/'program_manifest.json')
 assert len(config['seeds'])==30 and len(programs)==123
 for p in programs:assert sha(ROOT/p['file'])==p['sha256'],p['heuristic']
 return {'verified':True,'packaged_files':len(expected),'search_seeds':30,'final_candidates':120,'fixed_references':3}
def verify_bank():
 _,t,prior,*_=configure();raw={r['key']:r for r in load(ASSETS/'libraries/raw_fragments.json')}
 bank=load(ASSETS/'libraries/matched_random_fragments.json');index=prior.index()
 eligible=sorted((r for r in index['fragment_eligibility'] if r['eligible']),key=lambda r:r['key'])
 assert len(raw)==1947 and len(eligible)==len(bank)==1240
 assert len({r['key'] for r in bank})==1240
 for target,r in zip(eligible,bank):
  n=t.parse(r['expression']);assert r['template_key']==target['key']
  assert (r['type'],r['nodes'],r['depth'])==(target['type'],target['nodes'],target['depth'])
  assert (t.infer(n),t.size(n),t.depth(n),t.key(n))==(r['type'],r['nodes'],r['depth'],r['key'])
  assert t.key(t.canonical(n)) not in index['normalized']
 return {'verified':True,'historical_raw':1947,'eligible_each':1240,'full_roots_blocked':707,'oversize_slots_each':30,'AST_overlaps':sum(r['key'] in raw for r in bank)}
def replay(seeds=None):
 _,t,prior,g,gm,*_=configure();seeds=set(seeds or load(ROOT/'configs/study.json')['seeds'])
 initial=load(ASSETS/'initialization/results.json')
 ledger={r['id']:r for r in (json.loads(s) for s in (ROOT/'results/candidate_ledger.jsonl').read_text(encoding='utf-8').splitlines())}
 checks=0;runs=0
 for cohort in sorted((ROOT/'results/search').iterdir()):
  for checkpoint in sorted((cohort/'checkpoints').glob('*/checkpoint.json')):
   saved=load(checkpoint);method,seed=checkpoint.parent.name.rsplit('_',1);seed=int(seed)
   if seed not in seeds:continue
   module=gm if method=='matched_random_fragment_gp' else g
   population=g.selection([r for r in initial[str(seed)] if r['valid']]);best=population[0]
   seen={r['execution_key'] for r in initial[str(seed)]};library=module.load_library(method)
   assert len(saved['log'])==112
   for log in saved['log']:
    attempt=log['attempt'];child=module.offspring(seed,attempt,method,population,library);expected=ledger[child['id']]
    for key in ['execution_key','internal_key','expression','nodes','depth','operator','parent_id','second_parent_id','target_path','target_type','replacement_source','fragment_key','construction_error']:
     # Tuple components in AST paths become lists in the JSON archive.
     assert json.dumps(child.get(key),sort_keys=True)==json.dumps(expected.get(key),sort_keys=True),(method,seed,attempt,key)
    assert [r['id'] for r in population]==log['population_before']
    assert (child['execution_key'] in seen)==log['duplicate']
    if log['valid']:
     child.update(valid=True,mean_bins=log['mean_bins'])
     if g.order(child)<g.order(best):best=child
     if method!='fixed_parent_random':population=g.selection(population+[child])
    seen.add(child['execution_key'])
    assert best['id']==log['best_id'] and best['mean_bins']==log['best_mean_bins']
    assert [r['id'] for r in population]==log['population_after']
    checks+=1
   assert best['id']==saved['best']['id'] and best['execution_key']==saved['best']['execution_key']
   assert [r['id'] for r in population]==[r['id'] for r in saved['population']]
   runs+=1
   if runs%10==0:print(f'Replayed {runs} runs and {checks} archived attempts',flush=True)
 return {'runs':runs,'candidate_attempts':checks,'verified':True,'new_searches':0,'new_packing_evaluations':0,'new_LLM_calls':0}
def extract(output):
 _,t,*_=configure();registry=load(ASSETS/'sources/program_registry.json');raw={};clean={};converted=0;excluded=[]
 for row in registry:
  try:node,dependencies=t.expand_program((ASSETS/row['code_path']).read_text(encoding='utf-8'))
  except Exception as exc:
   assert not row['convertible'],row['program_id'];excluded.append({'program_id':row['program_id'],'error':type(exc).__name__+': '+str(exc)});continue
  assert row['convertible'] and t.key(node)==row['expression_key'],row['program_id'];converted+=1
  for path,part,kind in t.locations(node):
   key=t.key(part);canonical=t.canonical(part);ckey=t.key(canonical)
   origin={'program_id':row['program_id'],'expanded_path':list(path),'origin_multiplicity':max(1,len(row['origins']))}
   for store,k,n in [(raw,key,part),(clean,ckey,canonical)]:
    if k not in store:store[k]={'key':k,'expression':t.text(n),'type':t.infer(n),'size':t.size(n),'depth':t.depth(n),'sources':[]}
    store[k]['sources'].append(origin)
 archived_raw={r['key'] for r in load(ASSETS/'libraries/raw_fragments.json')};archived_clean={r['key'] for r in load(ASSETS/'libraries/clean_fragments.json')}
 assert set(raw)==archived_raw and set(clean)==archived_clean and converted==1166 and len(excluded)==76
 output=Path(output);save(output/'raw_fragments.json',list(raw.values()));save(output/'clean_fragments.json',list(clean.values()));save(output/'excluded.json',excluded)
 result={'source_programs':len(registry),'converted':converted,'excluded':len(excluded),'raw_unique':len(raw),'clean_unique':len(clean),'structural_keys_match_archives':True,'uses_archived_full_packing_acceptance':True,'new_LLM_calls':0}
 save(output/'extraction_audit.json',result);return result
