"""Documented, portable entry points. New outputs never rewrite archived results."""
import argparse,concurrent.futures,csv,datetime,json,os,shutil,subprocess,sys,time,warnings
from pathlib import Path
import numpy as np
from .runtime import ROOT,ASSETS,FROZEN,METHODS,configure,load,save,sha,new_output,prepare_runtime,identical_copy,external_module
from .analysis import summarize,write_csv,csvrows
from .audit import verify_files,verify_bank,replay,extract

def generate_data(output):
 output=new_output(output);c,*_=configure();generator=external_module('_dsai_official_generator',ROOT/'third_party/eoh/generate_instances.py')
 manifest=[]
 for split,seeds in [('pilot_dev',range(6001,6006)),('pilot_val',range(6101,6106)),('test_B',range(800001,800031))]:
  if split!='test_B':records=c.generator(split,seeds,5000)
  else:
   records=[{'id':f'B_fresh_{s}','seed':s,'distribution':'WB3S45_ROUND_C100_N5000_official','capacity':100,'num_items':5000,'items':generator.generate_weibull_dataset(1,5000,clipping_limit=100,seed=s)[5000][0]} for s in seeds]
  archived=load_jsonl(ASSETS/'data'/f'{split}.jsonl');assert len(records)==len(archived)
  for new,old in zip(records,archived):
   assert (new['id'],new['seed'],new['items'])==(old['id'],old['seed'],old['items'])
   manifest.append({'dataset':split,'instance_id':new['id'],'seed':new['seed'],'capacity':100,'num_items':5000,'rounding':'round' if split=='test_B' else 'floor','ordered_items_sha256':c.sha(np.asarray(new['items'],dtype='<i4').tobytes())})
  (output/f'{split}.jsonl').write_text(''.join(json.dumps(r,separators=(',',':'))+'\n' for r in records),encoding='utf-8')
 assert len({r['ordered_items_sha256'] for r in manifest})==40
 write_csv(output/'data_manifest.csv',manifest)
 result={'instances':40,'generated_items_match_saved_instances':True,'within_packaged_splits_overlap':0,'new_test_instances':False,'note':'Recreates existing viewed instances, not a new holdout.'};save(output/'audit.json',result);return result
def load_jsonl(path):return [json.loads(line) for line in Path(path).read_text(encoding='utf-8-sig').splitlines()]
def evaluate_worker(jobfile,outfile):
 job=load(jobfile);c,*_=configure();resource=c.memory_limit();p=job['program'];ns={'np':np}
 exec(compile(Path(job['file']).read_text(encoding='utf-8'),p['heuristic'],'exec'),ns)
 fn=ns.get('score',ns.get('heuristic'));rows=[];traces={}
 for instance in load_jsonl(ASSETS/'data'/f"{job['split']}.jsonl"):
  with warnings.catch_warnings(record=True) as ws:
   warnings.simplefilter('once');value,idx,caps=c.pack(instance,fn)
  rows.append({'dataset':'B_fresh' if job['split']=='test_B' else job['split'],'instance_id':instance['id'],'instance_seed':instance['seed'],
   'heuristic':p['heuristic'],'method':p['method'],'search_seed':p.get('search_seed'),'bins_used':value['bins_used'],'runtime':value['runtime'],'cpu_seconds':value['cpu_seconds'],
   'trace_hash':value['trace_hash'],'chosen_capacity_hash':value['chosen_capacity_hash'],'error':'','warnings':json.dumps(sorted(set(str(w.message) for w in ws)))})
  if job.get('save_traces'):traces['indices_'+instance['id']]=idx;traces['capacities_'+instance['id']]=caps
 if traces:np.savez_compressed(Path(outfile).with_suffix('.npz'),**traces)
 save(outfile,{'program':p['heuristic'],'resource':resource,'rows':rows})
def invoke_worker(mode,job,out,timeout=120):
 env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
 proc=subprocess.run([sys.executable,'-m','dsai',mode,str(job),str(out)],capture_output=True,text=True,encoding='utf-8',env=env,timeout=timeout)
 if proc.returncode:raise RuntimeError('Worker failed: '+proc.stderr[-2000:])
 return load(out)
def evaluate(output,split='test_B',workers=4,program_folder=None,only_references=False,compare=False,save_traces=False):
 output=new_output(output);start=time.perf_counter();programs=load(ASSETS/'program_manifest.json')
 if program_folder:
  programs=[p for p in programs if p['method']=='reference']
  for path in sorted(Path(program_folder).glob('*.py')):
   method,seed=path.stem.rsplit('_',1);assert method in METHODS
   programs.append({'heuristic':path.stem,'method':method,'search_seed':int(seed),'file':str(path.resolve()),'sha256':sha(path)})
 if only_references:programs=[p for p in programs if p['method']=='reference']
 if not programs:raise ValueError('No programs selected.')
 jobs=[]
 for p in programs:
  path=Path(p['file']);path=path if path.is_absolute() else ROOT/path
  assert sha(path)==p['sha256'];job=output/'jobs'/f"{p['heuristic']}.json";out=output/'workers'/f"{p['heuristic']}.json"
  save(job,{'program':p,'file':str(path.resolve()),'split':split,'save_traces':save_traces});out.parent.mkdir(exist_ok=True)
  jobs.append((job,out))
 with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
  completed=list(pool.map(lambda x:invoke_worker('_evaluate-worker',*x),jobs))
 rows=[r for x in completed for r in x['rows']];write_csv(output/'instance_results.csv',rows)
 if compare:
  if split!='test_B' or program_folder:raise ValueError('--compare-archived is only for the shipped B outputs.')
  saved={(r['heuristic'],r['instance_id']):r for r in csvrows(ROOT/'results/aggregate/all30_fourmethod_B_instance_results.csv')}
  for r in rows:
   old=saved[r['heuristic'],r['instance_id']]
   assert r['bins_used']==int(old['bins_used']) and r['trace_hash']==old['trace_hash'] and r['chosen_capacity_hash']==old['chosen_capacity_hash'],(r['heuristic'],r['instance_id'])
 result={'programs':len(programs),'instances_evaluated':len(rows),'split':split,'archived_bins_and_decision_hashes_match':True if compare else None,
  'wall_seconds':time.perf_counter()-start,'worker_count':workers,'new_searches':0,'new_LLM_calls':0,'environment':{'python':sys.version,'numpy':np.__version__,'os':sys.platform},'scope':'Re-evaluation on already viewed saved instances; runtimes are fresh.'}
 save(output/'evaluation_audit.json',result);return result
def conversion_worker(job,out):
 row=load(job)['program'];root=Path(out).resolve().parents[1];c,t,prior,g,gm,bank,pipeline=configure(root)
 c.data=lambda split:load_jsonl(ASSETS/'data'/f'{split}.jsonl')
 pipeline.extraction_worker(job,out)
 return load(out)
def conversion(output,limit=None,workers=4):
 output=new_output(output);rows=[r for r in load(ASSETS/'sources/program_registry.json') if r['convertible']]
 if limit:rows=rows[:limit]
 for d in ['traces','jobs','results','source_programs','extraction']:(output/d).mkdir(exist_ok=True)
 identical_copy(ASSETS/'extraction/score_probes.json',output/'extraction/score_probes.json');jobs=[]
 for r in rows:
  identical_copy(ASSETS/r['code_path'],output/r['code_path']);job=output/'jobs'/f"{r['program_id']}.json";out=output/'results'/f"{r['program_id']}.json"
  save(job,{'program':r});jobs.append((job,out))
 with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:results=list(pool.map(lambda pair:invoke_worker('_conversion-worker',*pair),jobs))
 assert all(r['valid'] for r in results),[r for r in results if not r['valid']][:1]
 result={'checked_programs':len(results),'full_corpus':limit is None,'full_pilot_score_and_packing_equivalence':True,'new_LLM_calls':0}
 save(output/'audit.json',result);return result
def rebuild_bank(output):
 output=new_output(output);*_,bank,pipeline=configure();bank.ROOT=output;bank.SOURCE=ASSETS;bank.main()
 created=load(output/'libraries/matched_random_fragments.json');archived=load(ASSETS/'libraries/matched_random_fragments.json')
 assert created==archived
 result={'entries':len(created),'all_entries_exactly_match_archived_bank':True,'new_searches':0,'new_LLM_calls':0};save(output/'reproduction_audit.json',result);return result
def run_search(output,seeds=None,methods=None,workers=4,resume=False):
 verify_files()
 config=load(ROOT/'configs/study.json');seeds=seeds or config['seeds'];methods=methods or list(METHODS)
 assert set(seeds)<=set(config['seeds']) and set(methods)<=set(METHODS)
 root=Path(output).resolve();settings={'seeds':seeds,'methods':methods,'workers':workers,'nominal_per_run':128,'new_per_run':112,'initial_evaluations':'reused frozen per-seed common initialization','manifest_sha256':sha(ROOT/'REPRODUCIBILITY_MANIFEST.json')}
 if resume:
  assert load(root/'portable_settings.json')==settings,'Resume settings changed.'
 root=prepare_runtime(root,resume);save(root/'portable_settings.json',settings)
 c,t,prior,g,gm,*_=configure(root);start=time.perf_counter()
 def one(pair):
  seed,method=pair;module=gm if method=='matched_random_fragment_gp' else g
  result=module.run_one(seed,method)
  save(root/'final_candidates'/f'{method}_{seed}.json',{'method':method,'seed':seed,'dev_mean':result['best']['mean_bins'],'execution_key':result['best']['execution_key']})
  (root/'final_candidates'/f'{method}_{seed}.py').write_text(t.program(g.dec(result['best']['tree'])),encoding='utf-8')
  return result
 with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:runs=list(pool.map(one,[(s,m) for s in seeds for m in methods]))
 selected=[{'method':r['method'],'seed':r['seed'],'initial_dev':r['initial_best']['mean_bins'],'final_dev':r['best']['mean_bins'],'candidate_id':r['best']['id'],'execution_key':r['best']['execution_key']} for r in runs]
 save(root/'outputs_freeze.json',{'selection':'pilot_dev only; frozen before pilot_val and B','selected':selected,'files':{p.name:sha(p) for p in (root/'final_candidates').glob('*.py')}})
 # Diagnostics follow all searches and output freezing, never parent or output selection.
 jobs=[]
 for r in runs:
  p=dict(r['best']);p['id']=f"final_{r['method']}_{r['seed']}";jobs.append(p)
 with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:diagnostics=list(pool.map(lambda p:g.evaluate(p,'pilot_val'),jobs))
 save(root/'pilot_val_diagnostic.json',diagnostics);write_csv(root/'run_summary.csv',selected)
 result={'runs':len(runs),'nominal_slots':128*len(runs),'new_child_slots':112*len(runs),'reused_initial_slots':16*len(runs),'wall_seconds_including_val_diagnostic':time.perf_counter()-start,'new_LLM_calls':0,'B_evaluated':False,'note':'New reproduction output, not appended to archived reported results.'}
 save(root/'execution_summary.json',result);return result
def main():
 parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
 sub.add_parser('verify');sub.add_parser('bank-audit')
 p=sub.add_parser('summarize');p.add_argument('--out')
 p=sub.add_parser('replay');p.add_argument('--seeds',nargs='+',type=int)
 for name in ['generate-data','extract','rebuild-bank']:
  p=sub.add_parser(name);p.add_argument('--out',required=True)
 p=sub.add_parser('verify-conversion');p.add_argument('--out',required=True);p.add_argument('--limit',type=int);p.add_argument('--workers',type=int,default=4)
 p=sub.add_parser('evaluate');p.add_argument('--out',required=True);p.add_argument('--split',choices=['pilot_dev','pilot_val','test_B'],default='test_B');p.add_argument('--workers',type=int,default=4);p.add_argument('--programs');p.add_argument('--references-only',action='store_true');p.add_argument('--compare-archived',action='store_true');p.add_argument('--save-traces',action='store_true')
 p=sub.add_parser('run');p.add_argument('--out',required=True);p.add_argument('--seeds',nargs='+',type=int);p.add_argument('--methods',nargs='+',choices=METHODS);p.add_argument('--workers',type=int,default=4);p.add_argument('--resume',action='store_true')
 for name in ['_evaluate-worker','_conversion-worker']:
  p=sub.add_parser(name);p.add_argument('job');p.add_argument('output')
 args=parser.parse_args()
 if hasattr(args,'workers') and not 1<=args.workers<=4:parser.error('workers must be between 1 and 4, matching the frozen resource envelope.')
 if getattr(args,'limit',None) is not None and args.limit<1:parser.error('--limit must be positive')
 command=args.command
 if command=='verify':result=verify_files()
 elif command=='bank-audit':result=verify_bank()
 elif command=='summarize':result=summarize(new_output(args.out) if args.out else None)
 elif command=='replay':result=replay(args.seeds)
 elif command=='generate-data':result=generate_data(args.out)
 elif command=='extract':result=extract(new_output(args.out))
 elif command=='rebuild-bank':result=rebuild_bank(args.out)
 elif command=='verify-conversion':result=conversion(args.out,args.limit,args.workers)
 elif command=='evaluate':result=evaluate(args.out,args.split,args.workers,args.programs,args.references_only,args.compare_archived,args.save_traces)
 elif command=='run':result=run_search(args.out,args.seeds,args.methods,args.workers,args.resume)
 elif command=='_evaluate-worker':evaluate_worker(args.job,args.output);return
 elif command=='_conversion-worker':conversion_worker(args.job,args.output);return
 print(json.dumps(result,ensure_ascii=False,indent=2))
