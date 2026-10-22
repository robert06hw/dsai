"""Verify, restore, evaluate, or reproduce the packaged position GP study."""
import os
for variable in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[variable]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
import argparse,csv,hashlib,importlib.util,json,shutil,subprocess,sys,zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
COHORTS={'original10':'fragment_position_gp_equal_time_01','extension20':'fragment_position_gp_equal_time_20seed_extension_01'}
CORE=ROOT/'fragment_gp_limited_01'

def load(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(path,value):Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rows(path):
    with Path(path).open(encoding='utf-8-sig',newline='') as stream:return list(csv.DictReader(stream))
def runtime():
    spec=importlib.util.spec_from_file_location('position_runtime',ROOT/COHORTS['original10']/'equal_time.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.CORE=CORE;module.ASSETS=ROOT/'assets'
    return module

def verify(deep=False):
    report=[]
    for name in [*COHORTS.values(),'fragment_gp_limited_01']:
        folder=ROOT/name;manifest=load(folder/'distribution_manifest.json')
        for relative,record in manifest['files'].items():
            assert sha(folder/relative)==record['sha256'],str(folder/relative)
        index=load(folder/'trace_archive_index.json')
        expected={entry['path']:entry for entry in index['members']}
        actual=set()
        for record in index['archives']:
            assert sha(folder/record['path'])==record['sha256'],record['path']
            with zipfile.ZipFile(folder/record['path']) as archive:
                for info in archive.infolist():
                    entry=expected[info.filename]
                    assert entry['archive']==record['path'] and info.file_size==entry['bytes']
                    assert info.filename not in actual
                    actual.add(info.filename)
                    if deep:assert hashlib.sha256(archive.read(info)).hexdigest()==entry['sha256'],info.filename
        assert actual==set(expected)
        report.append({'folder':name,'direct_files':len(manifest['files']),'archived_files':len(actual)})
    seeds=[]
    for name in COHORTS.values():seeds+=load(ROOT/name/'config.json')['search_seeds']
    assert len(seeds)==len(set(seeds))==30
    aggregate=ROOT/COHORTS['extension20']/'aggregate'
    results=rows(aggregate/'all30_threemethod_run_summary.csv')
    observations=rows(aggregate/'all30_threemethod_B_instance_results.csv')
    assert len(results)==90 and len(observations)==2790
    assert len({(r['method'],r['seed']) for r in results})==90
    assert sha(ROOT/COHORTS['original10']/'test_data/instances.jsonl')==sha(ROOT/COHORTS['extension20']/'test_data/instances.jsonl')
    return {'verified':True,'position_seeds':30,'position_runs':90,'instance_rows':2790,'folders':report,'deep_archive_check':deep}

def restore(destination):
    destination=Path(destination).resolve()
    if destination.exists():raise ValueError('Use a new output directory.')
    destination.mkdir(parents=True)
    for name in [*COHORTS.values(),'fragment_gp_limited_01']:
        source=ROOT/name;target=destination/name
        shutil.copytree(source,target,ignore=shutil.ignore_patterns('trace_archive_*.zip','__pycache__'))
        index=load(source/'trace_archive_index.json')
        for record in index['archives']:
            assert sha(source/record['path'])==record['sha256']
            with zipfile.ZipFile(source/record['path']) as archive:
                for info in archive.infolist():
                    final=(target/info.filename).resolve()
                    assert final.is_relative_to(target.resolve()),info.filename
                archive.extractall(target)
        for record in index['members']:assert sha(target/record['path'])==record['sha256'],record['path']
    return {'restored':True,'out':str(destination),'folders':3}

def evaluate(destination,smoke=False):
    destination=Path(destination).resolve()
    if destination.exists():raise ValueError('Use a new output directory.')
    destination.mkdir(parents=True)
    x=runtime();np,g,t,c,prior,v=x.modules()
    output=[];cache={};program_count=0
    for name in COHORTS.values():
        folder=ROOT/name;expected={(r['heuristic'],r['instance_id']):r for r in rows(folder/'test_instance_results.csv')}
        instances=[json.loads(line) for line in (folder/'test_data/instances.jsonl').read_text(encoding='utf-8').splitlines()]
        programs=load(folder/'test_programs.json')
        if smoke:
            cfg=load(folder/'config.json');seed=cfg['search_seeds'][0]
            programs=[p for p in programs if p['role']=='frozen_GP_output' and int(p['search_seed'])==seed]
            instances=instances[:1]
        for program in programs:
            source=folder/program['program'];digest=sha(source)
            assert digest==program['code_sha256']
            ns={'np':np};exec(compile(source.read_text(encoding='utf-8'),str(source),'exec'),ns)
            fn=ns['score'];program_count+=1
            for instance in instances:
                key=(digest,instance['id'])
                if key not in cache:
                    result,_,_=c.pack(instance,fn);cache[key]=result
                result=cache[key];old=expected[program['heuristic'],instance['id']]
                assert result['bins_used']==int(old['bins_used']),(name,program['heuristic'],instance['id'])
                assert result['trace_hash']==old['trace_hash']
                assert result['chosen_capacity_hash']==old['chosen_capacity_hash']
                output.append({'cohort':name,'heuristic':program['heuristic'],'instance_id':instance['id'],
                               'bins_used':result['bins_used'],'trace_hash':result['trace_hash'],'chosen_capacity_hash':result['chosen_capacity_hash']})
    with (destination/'instance_results.csv').open('w',encoding='utf-8',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(output[0]));writer.writeheader();writer.writerows(output)
    result={'passed':True,'mode':'smoke' if smoke else 'all_outputs','programs':program_count,'nominal_instance_rows':len(output),
            'physical_instance_evaluations':len(cache),'archived_bins_and_complete_decisions_match':True,'new_searches':0,'new_LLM_calls':0}
    save(destination/'audit.json',result);return result

def prepare_reproduction(cohort,destination):
    if sys.platform!='win32':raise ValueError('The archived process and memory controls require Windows.')
    destination=Path(destination).resolve()
    if destination.exists():raise ValueError('Use a new output directory.')
    destination.mkdir(parents=True);source=ROOT/COHORTS[cohort]
    for relative in ['config.json','initialization_plans.json','run_schedule.csv','process_control.py','frozen']:
        p=source/relative
        if p.is_dir():shutil.copytree(p,destination/relative)
        else:shutil.copyfile(p,destination/relative)
    text=(source/'equal_time.py').read_text(encoding='utf-8')
    text=text.replace('BASE=ROOT.parent','BASE=Path('+repr(str(ROOT))+')')
    text=text.replace("ASSETS=BASE/'dsai/assets'","ASSETS=BASE/'assets'")
    (destination/'equal_time.py').write_text(text,encoding='utf-8')
    registration=['config.json','initialization_plans.json','run_schedule.csv']+[p.relative_to(destination).as_posix() for p in (destination/'frozen').glob('*')]
    save(destination/'registration_lock.json',{'files':{p:sha(destination/p) for p in registration},'purpose':'New reproduction with saved seeds and initialization plans.'})
    dependencies=[p for p in CORE.glob('*.py')]+[CORE/'libraries/raw_fragments.json',CORE/'sources/historical_tree_index.json',ROOT/'assets/data/pilot_dev.jsonl']
    save(destination/'source_manifest.json',{'workspace_relative_paths':{p.relative_to(ROOT).as_posix():{'sha256':sha(p)} for p in dependencies}})
    save(destination/'execution_lock.json',{'registration_lock_sha256':sha(destination/'registration_lock.json'),
          'files':{p:sha(destination/p) for p in ['equal_time.py','process_control.py']},'purpose':'New reproduction; original execution locks are unchanged.'})
    save(destination/'reproduction.json',{'source_cohort':COHORTS[cohort],'source_runner_sha256':sha(source/'equal_time.py'),
          'path_changes':['BASE points to the cloned repository','ASSETS points to repository assets'],
          'run_count':load(destination/'config.json')['runs'],'seconds_per_run':120,'new_LLM_calls':0})
    return destination

def main():
    parser=argparse.ArgumentParser(description=__doc__);commands=parser.add_subparsers(dest='command',required=True)
    p=commands.add_parser('verify');p.add_argument('--deep',action='store_true')
    for name in ['restore','smoke','evaluate']:
        p=commands.add_parser(name);p.add_argument('--out',required=True)
    p=commands.add_parser('reproduce');p.add_argument('--cohort',choices=COHORTS,required=True);p.add_argument('--out',required=True);p.add_argument('--prepare-only',action='store_true')
    args=parser.parse_args()
    if args.command=='verify':result=verify(args.deep)
    elif args.command=='restore':result=restore(args.out)
    elif args.command in {'smoke','evaluate'}:result=evaluate(args.out,args.command=='smoke')
    else:
        destination=prepare_reproduction(args.cohort,args.out)
        if not args.prepare_only:subprocess.run([sys.executable,str(destination/'equal_time.py'),'search'],check=True)
        result={'prepared':True,'search_started':not args.prepare_only,'out':str(destination)}
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
