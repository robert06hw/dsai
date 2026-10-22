"""Frozen prior view: deny complete historical roots; diagnose rediscovery only."""
import collections, functools, json
from pathlib import Path
import cpu as c
import typed_tree as t
ROOT=Path(__file__).resolve().parent

def signature(instances):
    values=[[r['instance_id'],r['trace_hash'],r.get('chosen_capacity_hash',r.get('capacity_hash'))] for r in instances]
    return c.sha(json.dumps(values,separators=(',',':')))

def build_index():
    old=ROOT.parent/'fragment_gp_01';execution=collections.defaultdict(list);normal=collections.defaultdict(list);behavior=collections.defaultdict(list)
    source_records=[]
    for row in c.load(ROOT/'sources/program_registry.json'):
        if not row['convertible']:continue
        result=c.load(old/'extraction/results'/f"{row['program_id']}.json")
        if not result['valid']:continue
        node=t.parse(row['expression']);ek=t.key(node);nk=t.key(t.canonical(node));sig=signature(result['instances'])
        execution[ek].append(row['program_id']);normal[nk].append(row['program_id']);behavior[sig].append(row['program_id'])
        source_records.append({'program_id':row['program_id'],'expression':row['expression'],'execution_key':ek,'normalized_key':nk,
            'pilot_dev_mean':result['mean_bins'],'pilot_dev_behavior_signature':sig})
    fragments=c.load(ROOT/'libraries/raw_fragments.json');eligibility=[]
    for row in fragments:
        node=t.parse(row['expression']);nk=t.key(t.canonical(node));blocked=nk in normal
        eligibility.append({'key':row['key'],'type':row['type'],'eligible':not blocked,'nodes':t.size(node),'depth':t.depth(node),
            'reason':'complete historical score tree, including equivalent unary normalization' if blocked else 'proper subexpression not matching any full historical root',
            'matching_program_ids':normal.get(nk,[])})
    return {'source_programs_indexed':len(source_records),'historical_total_programs':1242,
        'coverage_note':'1166 supported/full-pilot_dev-verified histories; remaining76 have no supported score tree. No match does not prove novelty.',
        'execution':dict(execution),'normalized':dict(normal),'behavior':dict(behavior),'source_records':source_records,'fragment_eligibility':eligibility,
        'blocked_complete_roots':sum(not r['eligible'] for r in eligibility),'eligible_fragments':sum(r['eligible'] for r in eligibility),
        'fragment_size_policy':'unchanged: sampled fragment is checked inside emitted complete candidate <=64 nodes, depth<=8; no new independent smaller cap'}

@functools.lru_cache(maxsize=1)
def index():return c.load(ROOT/'sources/historical_tree_index.json')

def matches(node):
    row=index();ids=row['execution'].get(t.key(t.parse(t.text(node))),[])
    if ids:return {'historical_tree_class':'exact_existing_strategy','historical_tree_program_ids':ids}
    ids=row['normalized'].get(t.key(t.canonical(node)),[])
    if ids:return {'historical_tree_class':'normalized_existing_strategy','historical_tree_program_ids':ids}
    return {'historical_tree_class':'not_matched_supported_historical_tree','historical_tree_program_ids':[]}

def eligible_keys():return {r['key'] for r in index()['fragment_eligibility'] if r['eligible']}

def annotate_result(node,result):
    tree=matches(node);sig=signature(result['instances']) if result['valid'] else None
    group=index()['behavior'].get(sig,[]) if sig else []
    return {**tree,'historical_tree_rediscovered':bool(tree['historical_tree_program_ids']) and result['valid'],
        'observed_historical_behavior_signature':sig if group else None,'observed_historical_behavior_program_count':len(group),
        'observed_behavior_note':'matching complete pilot_dev decisions only; not universal semantic equivalence'}
