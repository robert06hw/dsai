"""Recompute reported statistics directly from the archived per-instance rows."""
import csv,collections,json
from pathlib import Path
import numpy as np
from .runtime import ROOT,load,save
def csvrows(path):
 with Path(path).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write_csv(path,rows):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);rows=list(rows)
 with path.open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]) if rows else []);w.writeheader();w.writerows(rows)
def summarize(output=None):
 base=ROOT/'results/aggregate';b=csvrows(base/'all30_fourmethod_B_instance_results.csv')
 search=csvrows(base/'all30_fourmethod_search_run_summary.csv')
 assert len(b)==3690 and len(search)==120 and not any(r['error'] for r in b)
 assert len({(r['heuristic'],r['instance_id']) for r in b})==3690
 methods=load(ROOT/'configs/study.json')['methods'];seeds=sorted({int(r['seed']) for r in search});ids=sorted({r['instance_id'] for r in b})
 assert len(seeds)==len(ids)==30
 matrices={m:np.zeros((30,30),dtype=float) for m in methods}
 lookup={(r['method'],int(r['search_seed']),r['instance_id']):int(r['bins_used']) for r in b if r['method']!='reference'}
 summary=[]
 for m in methods:
  for si,s in enumerate(seeds):
   for ii,i in enumerate(ids):matrices[m][si,ii]=lookup[m,s,i]
  rs=[r for r in search if r['method']==m];means=matrices[m].mean(axis=1)
  assert len(rs)==30 and {int(r['seed']) for r in rs}==set(seeds)
  summary.append({'method':m,'runs':30,'B_mean_bins':float(means.mean()),'B_seed_SD':float(means.std(ddof=1)),
   'mean_dev_final':float(np.mean([float(r['final_dev']) for r in rs])),
   'mean_val_diagnostic':float(np.mean([float(r['final_val_diagnostic']) for r in rs])),
   'dev_improved_runs':sum(float(r['gain_vs_initial_best'])>0 for r in rs),
   'valid_new':sum(int(r['valid_new']) for r in rs),'new_budget':3360,
   'mean_comparable_seconds':float(np.mean([float(r['comparable_run_wall_seconds']) for r in rs]))})
 rng=np.random.Generator(np.random.PCG64(900002));s=rng.integers(0,30,(10000,30));i=rng.integers(0,30,(10000,30))
 paired=[];archived=csvrows(base/'paired_cohort_summary.csv')
 for m in [m for m in methods if m!='raw_fragment_gp']:
  d=matrices[m]-matrices['raw_fragment_gp'];mean=d.mean(axis=1)
  boot=d[s[:,:,None],i[:,None,:]].mean(axis=(1,2));lo,hi=np.quantile(boot,[.025,.975])
  p={'control':m,'mean_delta_control_minus_raw':float(d.mean()),'raw_wins_seeds':int((mean>0).sum()),'ties_seeds':int((mean==0).sum()),'raw_losses_seeds':int((mean<0).sum()),'crossed_bootstrap_95_low':float(lo),'crossed_bootstrap_95_high':float(hi)}
  old=next(r for r in archived if r['control']==m and r['cohort']=='all30')
  for field,value in p.items():
   if field!='control':assert abs(value-float(old[field]))<1e-9,(m,field)
  paired.append(p)
 result={'run_rows':120,'B_rows':3690,'methods':summary,'paired':paired,'interval_scope':'descriptive; B reused; control introduced after earlier results; one random bank'}
 if output:
  output=Path(output);output.mkdir(parents=True,exist_ok=True)
  write_csv(output/'method_summary.csv',summary);write_csv(output/'paired_summary.csv',paired);save(output/'summary.json',result)
 return result
