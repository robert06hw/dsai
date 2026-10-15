"""Audit the bounded search ledger, summarize diagnostics, freeze portable outputs."""
import ast, collections, concurrent.futures, csv, datetime, json, sys
from pathlib import Path
import gp_search as g
import cpu as c
import typed_tree as t
import historical_prior as prior
import numpy as np
ROOT=Path(__file__).resolve().parent

def select(rows):
    rows=sorted(rows,key=lambda r:(r['mean_bins'],r['nodes'],r['execution_key']))
    keep=[];seen=set()
    for row in rows:
        if row['execution_key'] in seen:continue
        seen.add(row['execution_key']);keep.append(row)
        if len(keep)==16:break
    return keep

def dt(text):return datetime.datetime.fromisoformat(text)

def verify(root):
    root=Path(root).resolve();manifest=c.load(root/'manifest.json');actual={}
    def check(row):
        path=(root/row['path']).resolve();assert path.is_relative_to(root)
        data=path.read_bytes();h=c.sha(data);assert len(data)==row['bytes'] and h==row['sha256'],row['path']
        return row['path'],h
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:actual.update(pool.map(check,manifest['artifacts']))
    for name in ['pre_search_lock.json','execution_instrumentation_lock.json','experiment_lock.json']:
        for rel,h in c.load(root/name)['files'].items():assert actual[rel]==h,(name,rel)
    print(json.dumps({'verified':True,'root':str(root),'files':len(actual),'bytes':sum(r['bytes'] for r in manifest['artifacts']),
        'nominal_attempts':3840,'LLM_requests':0},ensure_ascii=False),flush=True)

def analyze():
    assert not (ROOT/'experiment_lock.json').exists(),'Frozen experiment; use verify'
    g.check_lock();config=c.load(ROOT/'config.json');assert config['nominal_total']==3840
    for rel,h in c.load(ROOT/'execution_instrumentation_lock.json')['files'].items():assert c.sha((ROOT/rel).read_bytes())==h,rel
    assert c.load(ROOT/'search_complete.json')['runs']==30
    plans=c.load(ROOT/'initialization/plans.json');initial=c.load(ROOT/'initialization/results.json')
    assert g.METHODS==['basic_gp','raw_fragment_gp','fixed_parent_random'] and g.SEEDS==[2323, 2424, 2525, 2626, 2727, 2828, 2929, 3030, 3131, 3232]
    historical_index=prior.index();allowed_fragments=prior.eligible_keys()
    search_complete=dt(c.load(ROOT/'search_complete.json')['completed_at'])
    lock_time=dt(c.load(ROOT/'pre_search_lock.json')['locked_at'])
    instrumentation_time=dt(c.load(ROOT/'execution_instrumentation_lock.json')['locked_at'])
    validation=c.load(ROOT/'diagnostic_validation.json');val_by_id={r['candidate']['id']:r['evaluation'] for r in validation}
    references_dev=c.load(ROOT/'diagnostic_reference_dev.json');reference_dev_by_id={r['candidate']['id']:r['evaluation'] for r in references_dev}
    for row in validation:assert dt(row['evaluation']['evaluation_started_at'])>=search_complete
    for row in references_dev:assert dt(row['evaluation']['evaluation_started_at'])>=search_complete
    summaries=[];attempt_rows=[];curves=[];parent_rows=[];instance_rows=[];initial_rows=[]
    physical_initial_eval=0;physical_child_eval=0;full_dev_workers=0;all_error=collections.Counter();plans_by_id={}
    rediscovery_rows=[];final_labels=[]
    def audit_result(p,result):
        nonlocal full_dev_workers
        assert result['id']==p['id'];assert dt(result['evaluation_started_at'])>=max(lock_time,instrumentation_time)
        assert dt(result['evaluation_completed_at'])>=dt(result['evaluation_started_at'])
        if not result.get('pre_evaluation_rejected') and not p.get('reference_name'):full_dev_workers+=result['split']=='pilot_dev'
        if not result['valid']:return
        assert len(result['instances'])==5 and (p.get('reference_name') or not g.limits(p))
        assert result['resource_limit']['enforced'] and result['resource_limit']['bytes']==536870912
        assert result['mean_bins']==float(np.mean([x['bins_used'] for x in result['instances']]))
        with np.load(ROOT/result['trace_path'],allow_pickle=False) as trace:
            for item in result['instances']:
                ix=trace['indices_'+item['instance_id']];caps=trace['capacities_'+item['instance_id']]
                assert ix.shape==caps.shape==(5000,)
                assert c.sha(np.asarray(ix,dtype='<i4').tobytes())==item['trace_hash']
                assert c.sha(np.asarray(caps,dtype='<i2').tobytes())==item['chosen_capacity_hash']
                assert np.max(ix)+1==item['bins_used']
                instance_rows.append({'candidate_id':p['id'],'dataset':result['split'],**item})
    for seed in g.SEEDS:
        values=initial[str(seed)];assert len(values)==16 and [r['id'] for r in values]==[r['id'] for r in plans[str(seed)]]
        seen=set()
        for p,row in zip(plans[str(seed)],values):
            assert p['source']==('Best-fit' if p['id'].endswith('_01') else 'basic_random')
            assert 'program_id' not in p and 'prior_pilot_dev_mean' not in p
            if p['source']=='basic_random':
                ordinal=int(p['id'].split('_')[-1]);r=g.rng(seed,ordinal,101)
                generated=t.random_tree('V',r,levels=int(r.integers(1,4)),safe=True)
                assert g.payload(generated)['execution_key']==p['execution_key']
            assert all(row[k]==p[k] for k in p)
            assert g.payload(g.dec(p['tree']))=={k:p[k] for k in g.payload(g.dec(p['tree']))}
            assert not g.limits(p)
            audit_result(p,c.load(ROOT/'evaluations'/f"pilot_dev_{p['id']}.json"));physical_initial_eval+=row['evaluation_wall_seconds']
            if p['source']=='Best-fit':assert row['mean_bins']==2066.4
            initial_rows.append({'seed':seed,'initial_slot':len([r for r in initial_rows if r['seed']==seed])+1,'id':p['id'],
                'source':p['source'],'program_id':p.get('program_id',''),'valid':row['valid'],'duplicate':p['execution_key'] in seen,
                'nodes':p['nodes'],'depth':p['depth'],'mean_bins':row.get('mean_bins'),'error':row['error'],
                'historical_tree_class':p['historical_tree_class']})
            seen.add(p['execution_key']);plans_by_id[p['id']]=row
        initial_best=select([r for r in values if r['valid']])[0]
        initial_wall=(max(dt(r['evaluation_completed_at']) for r in values)-min(dt(r['evaluation_started_at']) for r in values)).total_seconds()
        initial_cost=sum(r['evaluation_wall_seconds'] for r in values)
        for method in g.METHODS:
            folder=ROOT/'runs'/f'{method}_{seed}';complete=c.load(folder/'complete.json');state=c.load(folder/'checkpoint.json')
            assert complete['nominal_attempts']==128 and state['completed']==112 and len(state['log'])==112
            assert complete['initial_best']['id']==initial_best['id'] and complete['initial_best']['mean_bins']==initial_best['mean_bins']
            pop=select([r for r in values if r['valid']]);initial_ids=[r['id'] for r in pop];best=initial_best;seen={r['execution_key'] for r in values}
            parent_use=collections.Counter();receiver_use=collections.Counter();donor_use=collections.Counter();new_parent_events=0
            ops=collections.Counter();valids=duplicates=limits_failed=improved_parent=improved_initial=improved_current=fragments=0
            rediscovered=normalized_rediscovered=observed_same=0
            best_running=float('inf');cum=0
            for n,row in enumerate(values,1):
                if row['valid']:best_running=min(best_running,row['mean_bins'])
                cum+=row['evaluation_wall_seconds']
                curves.append({'method':method,'seed':seed,'nominal_slot':n,'new_attempt':0,'phase':'shared_initialization',
                    'best_mean_bins':best_running,'gain_vs_full_initial_best':initial_best['mean_bins']-best_running,
                    'cumulative_evaluation_seconds':cum,'cumulative_run_seconds_excluding_shared_init':0,
                    'comparable_wall_seconds':None})
                initial_annotation=prior.annotate_result(g.dec(row['tree']),row)
                if initial_annotation['historical_tree_rediscovered']:
                    rediscovery_rows.append({'method':method,'seed':seed,'phase':'shared_initialization','new_attempt':0,'nominal_slot':n,
                        'candidate_id':row['id'],'execution_key':row['execution_key'],'classification':initial_annotation['historical_tree_class'],
                        'historical_program_ids':';'.join(initial_annotation['historical_tree_program_ids']),'dev_mean_bins':row['mean_bins'],
                        'gain_vs_initial':initial_best['mean_bins']-row['mean_bins'],'operator':'initialization',
                        'replacement_source':row['source'],'target_path':'[]','cumulative_evaluation_seconds':cum,'cumulative_run_seconds':0})
            for attempt,log in enumerate(state['log'],1):
                p=c.load(ROOT/'candidates'/f'{method}_{seed}_{attempt:03d}.json');result=c.load(ROOT/'evaluations'/f"pilot_dev_{p['id']}.json")
                assert p['attempt']==attempt and p['seed']==seed and p['method']==method and p['id']==log['candidate_id']
                assert p['operator']==c.load(ROOT/'operator_schedule.json')[str(seed)][attempt-1]
                assert g.payload(g.dec(p['tree']))=={k:p[k] for k in g.payload(g.dec(p['tree']))}
                assert log['population_before']==[r['id'] for r in pop]
                assert p['parent_id'] in log['population_before'];parent=next(r for r in pop if r['id']==p['parent_id'])
                receiver_use[parent['id']]+=1;parent_use[parent['id']]+=1
                if parent['id'] not in initial_ids:new_parent_events+=1
                if p['operator']=='crossover':
                    assert p['second_parent_id'] in log['population_before'];donor_use[p['second_parent_id']]+=1;parent_use[p['second_parent_id']]+=1
                    if method=='fixed_parent_random':assert p['second_parent_id'] in initial_ids
                else:assert p['second_parent_id'] is None
                if method=='fixed_parent_random':assert p['parent_id'] in initial_ids
                if method=='basic_gp':assert p['replacement_source']!='historical_fragment'
                if p['replacement_source']=='historical_fragment':
                    fragments+=1;assert p['fragment_key'] in allowed_fragments
                    donor=next(r for r in historical_index['fragment_eligibility'] if r['key']==p['fragment_key'])
                    assert donor['eligible'] and not donor['matching_program_ids']
                assert log['duplicate']==(p['execution_key'] in seen);seen.add(p['execution_key'])
                audit_result(p,result);physical_child_eval+=result['evaluation_wall_seconds'];ops[p['operator']]+=1
                child={**p,**result};valid=result['valid'];assert log['valid']==valid and log['error']==result['error']
                annotation=prior.annotate_result(g.dec(p['tree']),result)
                assert p['historical_tree_class']==annotation['historical_tree_class']
                for field in ['historical_tree_class','historical_tree_rediscovered','observed_historical_behavior_signature','observed_historical_behavior_program_count']:
                    assert log[field]==annotation[field]
                rediscovered+=annotation['historical_tree_rediscovered']
                normalized_rediscovered+=valid and annotation['historical_tree_class']=='normalized_existing_strategy'
                observed_same+=valid and bool(annotation['observed_historical_behavior_program_count'])
                if annotation['historical_tree_rediscovered']:
                    rediscovery_rows.append({'method':method,'seed':seed,'phase':'new_child','new_attempt':attempt,'nominal_slot':16+attempt,
                        'candidate_id':p['id'],'execution_key':p['execution_key'],'classification':annotation['historical_tree_class'],
                        'historical_program_ids':';'.join(annotation['historical_tree_program_ids']),'dev_mean_bins':result['mean_bins'],
                        'gain_vs_initial':initial_best['mean_bins']-result['mean_bins'],'operator':p['operator'],
                        'replacement_source':p['replacement_source'],'target_path':json.dumps(p['target_path']),
                        'cumulative_evaluation_seconds':log['cumulative_evaluation_seconds'],'cumulative_run_seconds':log['cumulative_run_seconds']})
                assert log['mean_bins']==result.get('mean_bins')
                for tag,reference in [('parent',parent),('initial_best',initial_best),('previous_best',best)]:
                    expected=reference['mean_bins']-child['mean_bins'] if valid else None
                    assert log['delta_'+tag]==expected
                    assert log['improves_'+tag]==(valid and expected>0)
                if valid:
                    assert not g.limits(p)
                    if (child['mean_bins'],child['nodes'],child['execution_key'])<(best['mean_bins'],best['nodes'],best['execution_key']):best=child
                    if method!='fixed_parent_random':pop=select(pop+[child])
                assert log['population_after']==[r['id'] for r in pop] and len(pop)<=16
                assert log['best_id']==best['id'] and log['best_mean_bins']==best['mean_bins']
                valids+=valid;duplicates+=log['duplicate'];limits_failed+='SizeLimit' in result['error']
                improved_parent+=log['improves_parent'];improved_initial+=log['improves_initial_best'];improved_current+=log['improves_previous_best']
                if not valid:all_error[result['error']]+=1
                plans_by_id[p['id']]=child
                attempt_rows.append({'method':method,'seed':seed,**{k:x for k,x in log.items() if k not in {'population_before','population_after'}}})
                curves.append({'method':method,'seed':seed,'nominal_slot':16+attempt,'new_attempt':attempt,'phase':'offspring',
                    'best_mean_bins':best['mean_bins'],'gain_vs_full_initial_best':initial_best['mean_bins']-best['mean_bins'],
                    'cumulative_evaluation_seconds':log['cumulative_evaluation_seconds'],
                    'cumulative_run_seconds_excluding_shared_init':log['cumulative_run_seconds'],
                    'comparable_wall_seconds':initial_wall+log['cumulative_run_seconds']})
            assert ops=={'crossover':56,'subtree_replace':39,'constant_mutation':17}
            assert complete['best']['id']==best['id'] and complete['best']['mean_bins']==best['mean_bins']
            assert [r['id'] for r in complete['population']]==[r['id'] for r in pop]
            val=val_by_id[f'final_{method}_{seed}'];assert val['valid']
            candidate=next(r['candidate'] for r in validation if r['candidate']['id']==f'final_{method}_{seed}')
            assert candidate['selected_candidate_id']==best['id'] and candidate['execution_key']==best['execution_key']
            assert val['mean_bins']==float(np.mean([r['bins_used'] for r in val['instances']]))
            finalq=best['mean_bins'];first_new=0 if initial_best['mean_bins']==finalq else next(r['attempt'] for r in state['log'] if r['best_mean_bins']==finalq)
            final_annotation=prior.annotate_result(g.dec(best['tree']),best)
            final_labels.append({'method':method,'seed':seed,'selected_candidate_id':best['id'],**final_annotation})
            first_tree=next((r for r in state['log'] if r['historical_tree_rediscovered']),None)
            summary={'method':method,'seed':seed,'nominal_attempts':128,'new_attempts':112,'initial_valid':sum(r['valid'] for r in values),
                'initial_unique_valid':len(initial_ids),'initial_best_dev':initial_best['mean_bins'],'final_dev':finalq,
                'gain_vs_initial_best':initial_best['mean_bins']-finalq,'new_search_gain':finalq<initial_best['mean_bins'],
                'final_val_diagnostic':val['mean_bins'],'initial_best_val_diagnostic':val_by_id[f'initial_best_{seed}']['mean_bins'],
                'val_gain_vs_initial_diagnostic':val_by_id[f'initial_best_{seed}']['mean_bins']-val['mean_bins'],
                'valid_new':valids,'invalid_new':112-valids,'duplicate_new':duplicates,'size_rejected_new':limits_failed,
                'valid_rate_new':valids/112,'improved_parent_children':improved_parent,'improved_initial_children':improved_initial,
                'strict_new_best_updates':improved_current,'first_final_quality_new_attempt':first_new,
                'fragment_replacements':fragments,'descendant_receiver_events':new_parent_events,
                'distinct_receivers':len(receiver_use),'final_id':best['id'],'final_nodes':best['nodes'],'final_depth':best['depth'],
                'rediscovered_existing_tree_children':rediscovered,'normalized_rediscovery_children':normalized_rediscovered,
                'observed_existing_behavior_children':observed_same,'final_historical_tree_class':final_annotation['historical_tree_class'],
                'final_observed_behavior_program_count':final_annotation['observed_historical_behavior_program_count'],
                'first_any_existing_tree_new_attempt':first_tree['attempt'] if first_tree else None,
                'final_execution_key':best['execution_key'],'full_search_run_seconds':complete['actual_run_cumulative_seconds'],
                'shared_initial_wall_seconds':initial_wall,'comparable_run_wall_seconds':initial_wall+complete['actual_run_cumulative_seconds'],
                'nominal_cumulative_eval_seconds':state['cumulative_evaluation_seconds']}
            summaries.append(summary)
            for pid,count in parent_use.items():parent_rows.append({'method':method,'seed':seed,'parent_id':pid,'initial_parent':pid in initial_ids,
                'receiver_events':receiver_use[pid],'donor_events':donor_use[pid],'total_role_events':count,
                'dev_mean_bins':plans_by_id[pid]['mean_bins']})
            (ROOT/'final_candidates').mkdir(exist_ok=True)
            (ROOT/'final_candidates'/f'{method}_{seed}.py').write_text('import numpy as np\n\n'+t.program(g.dec(best['tree'])),encoding='utf-8')
    assert len(attempt_rows)==3360 and len(summaries)==30
    evaluation_files=list((ROOT/'evaluations').glob('*.json'));assert len(evaluation_files)==160+3360+46
    for row in validation+references_dev:
        p=row['candidate'];result=row['evaluation']
        # Reference source is trusted and quality-only; search size caps concern generated candidates.
        audit_result(p,result);assert result['valid']
    for name in ['raw_fragments']:
        assert c.sha((ROOT/'libraries'/f'{name}.json').read_bytes())==c.sha((g.OLD/'extraction'/f'{name}.json').read_bytes())
    assert c.sha((g.OLD/'manifest.json').read_bytes())==c.load(ROOT/'sources/extraction_integrity.json')['manifest_sha256']
    for path,rows in [('run_summary.csv',summaries),('attempt_results.csv',attempt_rows),('quality_curves.csv',curves),
        ('parent_reproduction.csv',parent_rows),('instance_results.csv',instance_rows),('initialization_summary.csv',initial_rows)]:c.table(ROOT/path,rows)
    c.table(ROOT/'rediscovered_strategy_events.csv',rediscovery_rows,fields=['method','seed','phase','new_attempt','nominal_slot','candidate_id','execution_key',
        'classification','historical_program_ids','dev_mean_bins','gain_vs_initial','operator','replacement_source','target_path','cumulative_evaluation_seconds','cumulative_run_seconds'])
    g.save(ROOT/'final_candidate_labels.json',final_labels)
    first_discovery=[];seen_discovery=set()
    for row in rediscovery_rows:
        key=(row['method'],row['seed'],row['execution_key'])
        if key not in seen_discovery:first_discovery.append(row);seen_discovery.add(key)
    c.table(ROOT/'first_rediscovery_costs.csv',first_discovery,fields=['method','seed','phase','new_attempt','nominal_slot','candidate_id','execution_key',
        'classification','historical_program_ids','dev_mean_bins','gain_vs_initial','operator','replacement_source','target_path','cumulative_evaluation_seconds','cumulative_run_seconds'])
    grouped=[]
    for method in g.METHODS:
        rows=[r for r in summaries if r['method']==method]
        grouped.append({'method':method,'seeds':10,'mean_initial_best_dev':float(np.mean([r['initial_best_dev'] for r in rows])),
            'mean_final_dev':float(np.mean([r['final_dev'] for r in rows])),'mean_gain_vs_initial':float(np.mean([r['gain_vs_initial_best'] for r in rows])),
            'mean_final_val_diagnostic':float(np.mean([r['final_val_diagnostic'] for r in rows])),
            'valid_new_total':sum(r['valid_new'] for r in rows),'duplicate_new_total':sum(r['duplicate_new'] for r in rows),
            'strict_new_best_updates_total':sum(r['strict_new_best_updates'] for r in rows),
            'runs_improved_initial':sum(r['new_search_gain'] for r in rows),
            'existing_tree_rediscovery_events':sum(r['rediscovered_existing_tree_children'] for r in rows),
            'mean_comparable_run_wall_seconds':float(np.mean([r['comparable_run_wall_seconds'] for r in rows]))})
    c.table(ROOT/'method_summary.csv',grouped)
    execution=c.load(ROOT/'execution_complete.json');environment=c.load(ROOT/'runtime_environment.json')
    cost={'nominal_total':3840,'physical_initial_attempts':160,'physical_new_child_attempts':3360,'physical_candidate_attempts':3520,
        'full_dev_search_worker_attempts':full_dev_workers,'diagnostic_val_attempts':43,'diagnostic_dev_reference_attempts':3,
        'physical_initial_evaluation_seconds_sum':physical_initial_eval,'physical_child_evaluation_seconds_sum':physical_child_eval,
        'diagnostic_evaluation_seconds_sum':sum(r['evaluation']['evaluation_wall_seconds'] for r in validation+references_dev),
        'experiment_wall_seconds':environment['invocation_including_instrumentation_wall_seconds'],
        'cost_note':'Per-run nominal initial cost repeated for fair curves; physical experiment cost includes shared init only once. Wall/evaluation sums differ under concurrency.',
        'LLM_requests':0,'LLM_tokens':0}
    g.save(ROOT/'cost_summary.json',cost)
    g.save(ROOT/'audit_checks.json',{'passed':True,'checked_at':c.now(),'nominal_3840_all_consumed':True,'new_attempts_3360':True,
        'shared_initial_identical':True,'Best_fit_plus15_basic_random_replayed':True,'no_complete_history_initial_injection':True,
        'unchanged_frozen_libraries':True,'full_historical_tree_fragment_insertion_forbidden_and_audited':True,'rediscovery_labels_and_costs_verified':True,
        'candidate_limits_enforced':True,'duplicates_valid_fully_evaluated':True,'no_hidden_retries':True,
        'operator_quotas_per_run_verified':True,'population_selection_replayed':True,'fixed_parents_never_updated':True,
        'parent_initial_current_improvement_flags_verified':True,'validation_only_after_all_searches':True,'full_saved_traces_rehashed':True,
        'LLM_requests':0,'LLM_tokens':0,'invalid_errors':dict(all_error)})
    from reporting import report
    (ROOT/'REPORT.md').write_text(report(config,summaries,grouped,initial_rows,cost,reference_dev_by_id,val_by_id,rediscovery_rows),encoding='utf-8')
    files=[p for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and not p.name.endswith('.tmp') and p.name not in {'manifest.json','experiment_lock.json'}]
    g.save(ROOT/'experiment_lock.json',{'frozen_at':c.now(),'nominal_attempts':3840,'LLM_requests':0,
        'files':{p.relative_to(ROOT).as_posix():c.sha(p.read_bytes()) for p in sorted(files)}})
    files.append(ROOT/'experiment_lock.json')
    g.save(ROOT/'manifest.json',{'experiment':'fragment_gp_limited_30seed_extension_01','nominal_attempts':3840,'LLM_requests':0,
        'artifacts':[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':c.sha(p.read_bytes())} for p in sorted(files)]})
    verify(ROOT)
    print(json.dumps(grouped,ensure_ascii=False),flush=True)

if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='verify':verify(sys.argv[2] if len(sys.argv)>2 else ROOT)
    else:analyze()
