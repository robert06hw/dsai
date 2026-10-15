"""Freeze the only new treatment; reuse the original30 shared initialization."""
import ast,concurrent.futures,hashlib,json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'fragment_gp_limited_30seed_extension_01'
ARCHIVES=[ROOT.parent/'fragment_gp_limited_01',ROOT.parent/'fragment_gp_limited_20seed_extension_01',SOURCE]
METHOD='matched_random_fragment_gp'
def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(rel,x):
    p=ROOT/rel;p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def change(s,a,b):assert a in s,a;return s.replace(a,b)
def copy(p,rel):
    p=Path(p)
    for archive in ARCHIVES:
        if p.is_relative_to(archive):
            name=p.relative_to(archive).as_posix()
            if name.startswith('aggregate/'):
                h=source_aggregate[archive].get(name[len('aggregate/'):])
                if h is not None:assert sha(p)==h
            elif name!='manifest.json':assert sha(p)==source_core[archive][name]['sha256']
            break
    dest=ROOT/rel;dest.parent.mkdir(exist_ok=True,parents=True);shutil.copy2(p,dest)
def funcs(s):return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(s).body if isinstance(n,ast.FunctionDef)}
def main():
    global source_core,source_aggregate
    source_core={a:{r['path']:r for r in load(a/'manifest.json')['artifacts']} for a in ARCHIVES}
    source_aggregate={a:load(a/'aggregate/manifest.json')['files'] if (a/'aggregate/manifest.json').exists() else {} for a in ARCHIVES}
    assert not (ROOT/'pre_search_lock.json').exists()
    assert load(ROOT.parent/'fragment_gp_mechanism_30seed_01/input_integrity.json')['passed']
    assert load(ROOT/'bank_match_audit.json')['exact_joint_distribution_match']
    seeds=load(SOURCE/'aggregate/scope.json')['all_seeds'];assert len(seeds)==30
    for name in ['cpu.py','typed_tree.py','historical_validator.py','historical_purity.py','scoring.py','historical_prior.py','timed_run.py']:
        copy(SOURCE/name,name)
    for rel in ['data/pilot_dev.jsonl','data/pilot_val.jsonl','data/reused_B.jsonl','libraries/raw_fragments.json','sources/historical_tree_index.json','sources/program_registry.json','sources/extraction_manifest.json','sources/previous_search_manifest.json','rules/Best-fit.py','rules/EoH.py','rules/Historical-best.py']:
        copy(SOURCE/rel,rel)
    for rel in ['aggregate/all30_B_instance_results.csv','aggregate/all30_search_run_summary.csv','aggregate/manifest.json','manifest.json']:
        copy(SOURCE/rel,'sources/previous30_'+rel.replace('/','_'))
    for rel in ['REPORT.md','input_integrity.json','manifest.json']:
        copy(ROOT.parent/'fragment_gp_mechanism_30seed_01'/rel,'sources/mechanism_'+rel)
    used={};plans={};results={};schedules={}
    for archive in ARCHIVES:
        manifest=load(archive/'manifest.json');entries={r['path']:r for r in manifest['artifacts']}
        def read(rel):
            p=archive/rel;r=entries[rel];assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],str(p)
            used[str(p)]={'sha256':r['sha256'],'bytes':r['bytes']};return load(p)
        pp=read('initialization/plans.json');rr=read('initialization/results.json');ss=read('operator_schedule.json')
        for seed in read('config.json')['seeds']:
            key=str(seed);assert key not in plans;plans[key]=pp[key];results[key]=rr[key];schedules[key]=ss[key]
            for row in rr[key]:
                rel=f"evaluations/pilot_dev_{row['id']}.json";result=read(rel);copy(archive/rel,rel)
                assert result['valid'] and result['id']==row['id']
                trace=result['trace_path'];r=entries[trace];assert sha(archive/trace)==r['sha256'];used[str(archive/trace)]=r;copy(archive/trace,trace)
    assert set(plans)==set(map(str,seeds)) and sum(map(len,plans.values()))==480
    save('initialization/plans.json',plans);save('initialization/results.json',results);save('operator_schedule.json',schedules)
    code=(SOURCE/'gp_search.py').read_text(encoding='utf-8')
    code=change(code,"METHODS=['basic_gp','raw_fragment_gp','fixed_parent_random']","METHODS=['matched_random_fragment_gp']")
    code=change(code,'SEEDS=[2323, 2424, 2525, 2626, 2727, 2828, 2929, 3030, 3131, 3232]','SEEDS='+repr(seeds))
    tree=ast.parse(code);prepare=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='prepare')
    lines=code.splitlines(True);lines[prepare.lineno-1:prepare.end_lineno]=["def prepare():\n    raise RuntimeError('Use setup_matched.py for frozen shared initialization')\n"]
    code=''.join(lines)
    tree=ast.parse(code);lib=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='load_library')
    lines=code.splitlines(True);lines[lib.lineno-1:lib.end_lineno]=["def load_library(method):\n    assert method=='matched_random_fragment_gp'\n    out=collections.defaultdict(list)\n    rows=c.load(ROOT/'libraries/matched_random_fragments.json')\n    for row in sorted(rows,key=lambda r:r['template_key']):\n        node=t.parse(row['expression']);assert t.key(node)==row['key']\n        out[row['type']].append((node,row['key']))\n    return out\n"]
    code=''.join(lines);code=change(code,"replacement_source='historical_fragment'","replacement_source='matched_random_fragment'")
    (ROOT/'gp_search.py').write_text(code,encoding='utf-8')
    before=funcs((SOURCE/'gp_search.py').read_text(encoding='utf-8'));after=funcs(code)
    unchanged=[k for k in before if k not in ['prepare','load_library','offspring']];assert all(before[k]==after[k] for k in unchanged)
    normalized=code.replace("replacement_source='matched_random_fragment'","replacement_source='historical_fragment'")
    assert funcs(normalized)['offspring']==before['offspring']
    timing=(ROOT/'timed_run.py').read_text(encoding='utf-8')
    timing=change(timing,"assert not list((ROOT/'evaluations').glob('*.json')),'Instrumentation must be locked before first candidate evaluation'", "assert all(p.name.startswith('pilot_dev_init_') for p in (ROOT/'evaluations').glob('*.json')),'Only locked, reused initialization evaluations may precede instrumentation'")
    (ROOT/'timed_run.py').write_text(timing,encoding='utf-8')
    analysis=(SOURCE/'analyze.py').read_text(encoding='utf-8')
    analysis=change(analysis,"g.METHODS==['basic_gp','raw_fragment_gp','fixed_parent_random'] and g.SEEDS==[2323, 2424, 2525, 2626, 2727, 2828, 2929, 3030, 3131, 3232]","g.METHODS==['matched_random_fragment_gp'] and g.SEEDS=="+repr(seeds))
    analysis=change(analysis,'allowed_fragments=prior.eligible_keys()',"matched_bank={r['key']:r for r in c.load(ROOT/'libraries/matched_random_fragments.json')};allowed_fragments=set(matched_bank)")
    analysis=change(analysis,"assert result['id']==p['id'];assert dt(result['evaluation_started_at'])>=max(lock_time,instrumentation_time)","assert result['id']==p['id']\n        if not p['id'].startswith('init_'):assert dt(result['evaluation_started_at'])>=max(lock_time,instrumentation_time)\n        else:\n            rel=f\"evaluations/pilot_dev_{p['id']}.json\";assert c.sha((ROOT/rel).read_bytes())==c.load(ROOT/'pre_search_lock.json')['files'][rel]")
    analysis=change(analysis,"and not p.get('reference_name'):full_dev_workers", "and not p.get('reference_name') and not p['id'].startswith('init_'):full_dev_workers")
    analysis=analysis.replace("=='historical_fragment'","=='matched_random_fragment'").replace("!='historical_fragment'","!='matched_random_fragment'")
    analysis=change(analysis,"donor=next(r for r in historical_index['fragment_eligibility'] if r['key']==p['fragment_key'])\n                    assert donor['eligible'] and not donor['matching_program_ids']", "donor=matched_bank[p['fragment_key']]\n                    assert t.key(t.canonical(t.parse(donor['expression']))) not in historical_index['normalized']")
    analysis=change(analysis,'160+3360+46','480+3360+66')
    analysis=change(analysis,"'seeds':10","'seeds':30")
    analysis=change(analysis,"'physical_initial_attempts':160","'physical_initial_attempts':0,'reused_initial_slots':480")
    analysis=change(analysis,"'physical_candidate_attempts':3520","'physical_candidate_attempts':3360")
    analysis=change(analysis,"'diagnostic_val_attempts':43","'diagnostic_val_attempts':63")
    analysis=change(analysis,"'physical_initial_evaluation_seconds_sum':physical_initial_eval","'physical_initial_evaluation_seconds_sum':0,'reused_initial_evaluation_seconds_sum':physical_initial_eval,'bank_build_wall_seconds':c.load(ROOT/'bank_match_audit.json')['bank_build_wall_seconds']")
    analysis=analysis.replace("'fixed_parents_never_updated':True","'population_updates_match_historical_GP':True")
    analysis=analysis.replace("'experiment':'fragment_gp_limited_30seed_extension_01'","'experiment':'matched_random_fragment_gp_30seed_01'")
    (ROOT/'analyze.py').write_text(analysis,encoding='utf-8')
    for file in ['gp_search.py','timed_run.py','analyze.py']:compile((ROOT/file).read_text(encoding='utf-8'),file,'exec')
    sys.path.insert(0,str(ROOT));import gp_search as g
    save('operator_checks.json',g.operator_test())
    save('sources/extraction_integrity.json',{'passed':True,'manifest_sha256':sha(g.OLD/'manifest.json'),'source':'Previously sealed, unchanged historical fragment extraction; only matched bank is new.'})
    config=load(SOURCE/'config.json');config.update(seeds=seeds,methods=[METHOD],nominal_total=3840,shared_initial_physical_attempts=0,new_child_attempts=3360,reused_initial_slots=480,
        random_library_count=1240,library='Frozen matched_random_fragments.json; only type/size/depth matched, one bank realization',fixed_parent_library='Archived control only, no new fixed-parent search')
    save('config.json',config)
    save('sources/matched_change_record.json',{'source_30seed_core_manifest_sha256':sha(SOURCE/'manifest.json'),'source_30seed_aggregate_manifest_sha256':sha(SOURCE/'aggregate/manifest.json'),
        'read_source_files_verified':used,'seeds':seeds,'new_runs':30,'nominal_total':3840,'new_candidate_attempts':3360,'reused_initial_slots':480,
        'unchanged_function_ASTs':unchanged,'offspring_AST_identical_except_origin_label':True,'changes':'Only matched typed library load, origin log label, initialization reuse and bookkeeping; same offspring RNG/operators, evaluation and selection.',
        'bank_sha256':sha(ROOT/'libraries/matched_random_fragments.json'),'bank_audit_sha256':sha(ROOT/'bank_match_audit.json'),
        'stage1_complete_before_new_search':True,'B_data_role':'Same already-viewed B30; no new holdout. Method requested after observing old30 outcomes.','LLM_requests':0})
    files=[p for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.tmp']
    save('pre_search_lock.json',{'locked_at':g.c.now(),'files':{p.relative_to(ROOT).as_posix():sha(p) for p in files}})
    print('Matched GP locked: original30 seeds,480 reused init slots,3360 new attempts,one new method.',flush=True)
if __name__=='__main__':main()
