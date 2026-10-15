"""Post-search candidate-size/validity diagnostics, no packing or selection."""
import collections,csv,hashlib,json,shutil
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
BASE=HERE.parent if HERE.name=='matched_random_fragment_gp_30seed_01' else HERE
ROOT=BASE/'matched_random_fragment_gp_30seed_01'
ARCHIVES=[BASE/'fragment_gp_limited_01',BASE/'fragment_gp_limited_20seed_extension_01',BASE/'fragment_gp_limited_30seed_extension_01']
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def table(name,rows):
    with (ROOT/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
assert load(ROOT/'search_complete.json')['runs']==30
all_rows=[];historical_plans={};source_by_seed={}
for archive in ARCHIVES:
    for seed in load(archive/'config.json')['seeds']:source_by_seed[seed]=archive
    with (archive/'attempt_results.csv').open(encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            for k in ['nodes','depth','seed','attempt']:r[k]=int(r[k])
            for k in ['valid','duplicate']:r[k]=r[k]=='True'
            all_rows.append(r)
for path in (ROOT/'runs').glob('*/checkpoint.json'):
    seed=int(path.parent.name.split('_')[-1])
    all_rows.extend({'method':'matched_random_fragment_gp','seed':seed,**r} for r in load(path)['log'])
methods=['basic_gp','raw_fragment_gp','fixed_parent_random','matched_random_fragment_gp'];rows=[]
for m in methods:
    rr=[r for r in all_rows if r['method']==m];assert len(rr)==3360
    good=[r for r in rr if r['valid']];n=np.asarray([r['nodes'] for r in rr]);d=np.asarray([r['depth'] for r in rr])
    rows.append({'method':m,'candidate_attempts':3360,'valid':len(good),'invalid':3360-len(good),'valid_rate':len(good)/3360,'duplicates':sum(r['duplicate'] for r in rr),
                 'size_limit_rejections':sum('SizeLimit' in r['error'] for r in rr),'construction_rejections':sum('ConstructionFailure' in r['error'] for r in rr),
                 'all_mean_nodes':float(n.mean()),'all_median_nodes':float(np.median(n)),'all_p90_nodes':float(np.quantile(n,.9)),'all_max_nodes':int(n.max()),
                 'all_mean_depth':float(d.mean()),'all_median_depth':float(np.median(d)),'all_p90_depth':float(np.quantile(d,.9)),
                 'valid_mean_nodes':float(np.mean([r['nodes'] for r in good])),'valid_mean_depth':float(np.mean([r['depth'] for r in good]))})
table('candidate_size_summary.csv',rows)
dist=[]
for m in methods:
    counts=collections.Counter((r['nodes'],r['depth'],r['valid']) for r in all_rows if r['method']==m)
    dist.extend({'method':m,'nodes':n,'depth':d,'valid':v,'count':c} for (n,d,v),c in sorted(counts.items()))
table('candidate_size_distribution.csv',dist)
bank={r['key']:r for r in load(ROOT/'libraries/matched_random_fragments.json')}
hist={(r['seed'],r['attempt']):r for r in all_rows if r['method']=='raw_fragment_gp'}
new=[r for r in all_rows if r['method']=='matched_random_fragment_gp'];pairs=[]
for row in new:
    old=hist[row['seed'],row['attempt']]
    if old['replacement_source']=='historical_fragment' and row['replacement_source']=='matched_random_fragment':
        op=load(source_by_seed[row['seed']]/'candidates'/f"raw_fragment_gp_{row['seed']}_{row['attempt']:03d}.json")
        np_=load(ROOT/'candidates'/f"matched_random_fragment_gp_{row['seed']}_{row['attempt']:03d}.json")
        slot=bank[row['fragment_key']];same_type=op['target_type']==np_['target_type'];same_template=slot['template_key']==old['fragment_key']
        if same_type:assert same_template
        pairs.append({'seed':row['seed'],'attempt':row['attempt'],'historical_target_type':op['target_type'],'matched_target_type':np_['target_type'],'same_target_type':same_type,
                      'same_template_slot':same_template,'historical_fragment_key':old['fragment_key'],'matched_fragment_key':row['fragment_key'],
                      'historical_candidate_nodes':old['nodes'],'matched_candidate_nodes':row['nodes'],'historical_candidate_depth':old['depth'],'matched_candidate_depth':row['depth'],
                      'historical_candidate_valid':old['valid'],'matched_candidate_valid':row['valid']})
table('paired_library_draws.csv',pairs)
(ROOT/'candidate_size_audit.json').write_text(json.dumps({'passed':True,'all_four_methods_attempts':13440,'same_type_draws_have_identical_matched_template_slot':True,
    'paired_successful_library_draws':len(pairs),'same_target_type_draws':sum(r['same_target_type'] for r in pairs),'source':'Sealed old attempt_results and new complete checkpoints; diagnostics only, no quality filtering.'},ensure_ascii=False,indent=2),encoding='utf-8')
shutil.copy2(Path(__file__),ROOT/'candidate_size_analysis.py')
print(json.dumps(rows,ensure_ascii=False),flush=True)
