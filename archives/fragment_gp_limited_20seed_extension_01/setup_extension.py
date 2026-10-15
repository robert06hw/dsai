"""Prepare a seed-only extension, preserving frozen search algorithms."""
import ast, difflib, hashlib, json, shutil, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OLD=ROOT.parent/'fragment_gp_limited_01'
TEST=ROOT.parent/'fragment_gp_limited_test_01'
SEEDS=list(range(606,2223,101))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def save(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def copy(rel,target=None):
    dest=ROOT/(target or rel);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(OLD/rel,dest)
def replace(text,old,new):
    assert old in text,old
    return text.replace(old,new)
def main():
    assert not (ROOT/'pre_search_lock.json').exists(),'Cannot change a locked extension'
    assert len(SEEDS)==17 and not set(SEEDS)&{303,404,505}
    for folder in [OLD,TEST]:
        manifest=load(folder/'manifest.json')
        for row in manifest['artifacts']:
            p=folder/row['path'];assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],str(p)
    for name in ['cpu.py','typed_tree.py','historical_validator.py','historical_purity.py','scoring.py','historical_prior.py','timed_run.py']:
        copy(name)
    for rel in ['data/pilot_dev.jsonl','data/pilot_val.jsonl','libraries/raw_fragments.json',
                'sources/program_registry.json','sources/extraction_manifest.json',
                'sources/previous_search_manifest.json','sources/historical_tree_index.json',
                'rules/Best-fit.py','rules/EoH.py','rules/Historical-best.py']:
        copy(rel)
    for rel in ['config.json','manifest.json','run_summary.csv','method_summary.csv']:
        copy(rel,'sources/original_limited_'+rel.replace('.','_')+'.json' if rel.endswith('.json') else 'sources/original_limited_'+rel)
    gp=(OLD/'gp_search.py').read_text(encoding='utf-8')
    gp=replace(gp,'SEEDS=[303,404,505]','SEEDS='+repr(SEEDS))
    gp=replace(gp,"'nominal_total':1152,'shared_initial_physical_attempts':48,'new_child_attempts':1008", "'nominal_total':6528,'shared_initial_physical_attempts':272,'new_child_attempts':5712")
    gp=replace(gp,"'runs':9,'nominal_attempts':1152,'new_child_attempts':1008", "'runs':51,'nominal_attempts':6528,'new_child_attempts':5712")
    gp=replace(gp,"'nominal_attempts':1152", "'nominal_attempts':6528")
    gp=replace(gp,'All nine limited-initialization searches and diagnostics complete','All 51 seed-extension searches and diagnostics complete')
    gp=replace(gp,'three new seeds, Best-fit+15random initial','17 additional seeds, unchanged Best-fit+15random initial')
    (ROOT/'gp_search.py').write_text(gp,encoding='utf-8')
    analysis=(OLD/'analyze.py').read_text(encoding='utf-8')
    replacements=[('==[303,404,505]','=='+repr(SEEDS)),('==9','==51'),
       ('48+1008+18','272+5712+74'),("'seeds':3","'seeds':17"),
       ("'physical_initial_attempts':48","'physical_initial_attempts':272"),
       ("'diagnostic_val_attempts':15","'diagnostic_val_attempts':71"),
       ('1152','6528'),('1008','5712'),('1056','5984'),
       ("'experiment':'fragment_gp_limited_01'","'experiment':'fragment_gp_limited_20seed_extension_01'")]
    for a,b in replacements:analysis=replace(analysis,a,b)
    (ROOT/'analyze.py').write_text(analysis,encoding='utf-8')
    def functions(text):
        return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)}
    before=functions((OLD/'gp_search.py').read_text(encoding='utf-8'));after=functions(gp)
    unchanged=[n for n in before if n not in ['prepare','run']]
    assert all(before[n]==after[n] for n in unchanged),'Seed extension modified a search algorithm'
    for name in ['cpu.py','typed_tree.py','historical_validator.py','historical_purity.py','scoring.py','historical_prior.py','timed_run.py']:
        assert sha(ROOT/name)==sha(OLD/name)
    # Preserve the complete historical eligibility view byte-for-byte, not rebuilt from new outputs.
    save(ROOT/'sources/extension_change_record.json',{'seeds':SEEDS,'new_runs':51,'new_nominal_slots':6528,
       'new_physical_candidate_attempts':5984,'old_seed_results_reused':True,
       'unchanged_search_function_ASTs':unchanged,'byte_identical_helpers':['cpu.py','typed_tree.py','historical_validator.py','historical_purity.py','scoring.py','historical_prior.py','timed_run.py'],
       'original_limited_manifest_sha256':sha(OLD/'manifest.json'),'original_test_manifest_sha256':sha(TEST/'manifest.json'),
       'raw_fragment_sha256':sha(ROOT/'libraries/raw_fragments.json'),
       'historical_tree_index_sha256':sha(ROOT/'sources/historical_tree_index.json'),
       'allowed_code_changes':'Seed list, run and accounting counts, completion text and descriptive reports only. No search algorithm or hyperparameter changed.',
       'B_data_role':'Reuse already-viewed 30 B instances for comparable expanded seed diagnostics. This is post-result seed extension, not a new untouched holdout.'})
    diffs=[]
    for name in ['gp_search.py','analyze.py']:
        diffs.extend(difflib.unified_diff((OLD/name).read_text(encoding='utf-8').splitlines(True),
                     (ROOT/name).read_text(encoding='utf-8').splitlines(True),fromfile='original/'+name,tofile='extension/'+name))
    (ROOT/'sources/seed_extension.diff').write_text(''.join(diffs),encoding='utf-8')
    for folder in ['initialization','candidates','jobs','evaluations','traces','runs','final_candidates']:
        (ROOT/folder).mkdir(exist_ok=True)
    dest=ROOT/'data/reused_B.jsonl';shutil.copy2(TEST/'data/test_B.jsonl',dest)
    for name in ['program_registry.json','data_manifest.csv','config.json','outputs_freeze.json','evaluation_lock.json','manifest.json','nonoverlap_audit.json']:
        target=ROOT/'sources'/('original_B_'+name);shutil.copy2(TEST/name,target)
    sys.path.insert(0,str(ROOT));import gp_search as g
    # Exactly the old frozen prior, no new bank material and no new behavior groups.
    original_index=load(ROOT/'sources/historical_tree_index.json')
    g.prior.build_index=lambda:original_index
    g.prepare()
    assert sha(ROOT/'sources/historical_tree_index.json')==sha(OLD/'sources/historical_tree_index.json')
    config=load(ROOT/'config.json');old_config=load(OLD/'config.json')
    changed={'seeds','nominal_total','shared_initial_physical_attempts','new_child_attempts'}
    assert all(config[k]==old_config[k] for k in old_config if k not in changed), 'Hyperparameters differ'
    print('17-seed extension ready. Algorithms and all non-accounting settings unchanged.',flush=True)
if __name__=='__main__':main()
