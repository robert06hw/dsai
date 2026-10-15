"""Locations, immutable sources and portable execution workspaces."""
from pathlib import Path
import functools,hashlib,importlib,importlib.util,json,os,shutil,sys
ROOT=Path(__file__).resolve().parents[2]
ASSETS=ROOT/'assets'
FROZEN=Path(__file__).resolve().parent/'frozen'
METHODS=('basic_gp','raw_fragment_gp','fixed_parent_random','matched_random_fragment_gp')
def load(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(path,value):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
def external_module(name,path):
 spec=importlib.util.spec_from_file_location(name,str(path));m=importlib.util.module_from_spec(spec)
 sys.modules[name]=m;spec.loader.exec_module(m);return m
@functools.lru_cache(maxsize=1)
def modules():
 sys.path.insert(0,str(FROZEN))
 cpu=importlib.import_module('cpu');typed=importlib.import_module('typed_tree');prior=importlib.import_module('historical_prior')
 old=external_module('_dsai_archived_gp',FROZEN/'gp_search_historical.py')
 matched=external_module('_dsai_archived_matched_gp',FROZEN/'gp_search_matched.py')
 bank=external_module('_dsai_archived_bank',FROZEN/'build_random_bank.py')
 extraction=external_module('_dsai_archived_extraction',FROZEN/'extraction_pipeline.py')
 return cpu,typed,prior,old,matched,bank,extraction
def configure(root=ASSETS):
 cpu,typed,prior,old,matched,bank,extraction=modules();root=Path(root).resolve()
 for m in [cpu,prior,old,matched,extraction]:m.ROOT=root
 prior.index.cache_clear()
 return cpu,typed,prior,old,matched,bank,extraction
def new_output(path,resume=False):
 path=Path(path).resolve()
 immutable=[ROOT/'assets',ROOT/'archives',ROOT/'results',ROOT/'provenance',ROOT/'reports',ROOT/'src',ROOT/'third_party',ROOT/'docs']
 if path==ROOT or any(path.is_relative_to(p) or p.is_relative_to(path) for p in immutable):
  raise ValueError('Choose a fresh output under runs/ or outside the repository; immutable inputs cannot be overwritten.')
 if path.exists() and any(path.iterdir()) and not resume:raise ValueError('Output is nonempty; choose a new directory or use the documented --resume option.')
 path.mkdir(parents=True,exist_ok=True);return path
def identical_copy(source,dest):
 source=Path(source);dest=Path(dest);dest.parent.mkdir(parents=True,exist_ok=True)
 if dest.exists():
  if sha(source)!=sha(dest):raise ValueError('Different existing execution input: '+str(dest))
 else:shutil.copy2(source,dest)
def prepare_runtime(path,resume=False):
 root=new_output(path,resume)
 for name in ['cpu.py','typed_tree.py','historical_validator.py','historical_purity.py','scoring.py','historical_prior.py']:
  identical_copy(FROZEN/name,root/name)
 # Both archived search modules have the same worker AST. This unchanged file is
 # only a subprocess worker entry; orchestration calls each original run_one.
 identical_copy(FROZEN/'gp_search_historical.py',root/'gp_search.py')
 for directory in ['data','rules','libraries','sources','initialization']:
  for p in (ASSETS/directory).rglob('*'):
   if p.is_file():identical_copy(p,root/directory/p.relative_to(ASSETS/directory))
 identical_copy(ASSETS/'operator_schedule.json',root/'operator_schedule.json')
 for directory in ['runs','candidates','evaluations','jobs','traces','final_candidates']:(root/directory).mkdir(exist_ok=True)
 return root
