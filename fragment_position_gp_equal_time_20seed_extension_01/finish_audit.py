"""Read-only scientific/timing checks after search and frozen-output testing."""
import collections,csv,json,time
from pathlib import Path
import equal_time as x
ROOT=x.ROOT

def main():
    start=time.perf_counter();x.verify_lock();cfg=x.load(ROOT/'config.json');out=x.load(ROOT/'outputs_freeze.json')
    assert out['completed_runs']==cfg['runs']
    for rel,h in out['files'].items():assert x.sha(ROOT/rel)==h
    assert cfg['user_requested_additional_seeds']==20
    np,g,t,c,prior,v=x.modules();summary=x.load(ROOT/'search_summary.json');assert len(summary)==cfg['runs']
    init={};audit_rows=[];all_io=[];parent_rows=[]
    for rec in summary:
        folder=ROOT/'runs'/f"{rec['method']}_{rec['seed']}";launch=x.load(folder/'launch.json')
        assert 119.9<=rec['scheduler_stop_elapsed']<125 and rec['last_commit_elapsed']<120
        assert rec['initial_completed']==16 and rec['best'] and rec['best']['valid']
        initial=[x.load(p) for p in sorted((folder/'initialization').glob('*.json'))];assert len(initial)==16
        signature=[(r['execution_key'],r['valid'],r.get('mean_bins'),[i.get('trace_hash') for i in r.get('instances',[])]) for r in initial]
        if rec['seed'] in init:assert init[rec['seed']]==signature,'Initial fitness/validity differs within pair'
        else:init[rec['seed']]=signature
        commits=[]
        for marker in sorted((folder/'commits').glob('*.commit')):
            row=x.load(marker);p=marker.with_suffix('.json');assert x.sha(p)==row['snapshot_sha256']
            assert row['committed_perf']<launch['deadline'];commits.append((row,p))
        assert len(commits)==16+rec['offspring_completed']
        last=x.load(commits[-1][1]);assert last['best']['execution_key']==rec['best']['execution_key']
        assert last['best']['worker_finished_perf']<commits[-1][0]['committed_perf']<launch['deadline']
        assert len(last['population'])<=16 and len({p['execution_key'] for p in last['population']})==len(last['population'])
        assert last['population']==g.selection(last['population'])
        assert not g.limits(g.payload(g.dec(last['best']['tree'])))
        # All completed child decisions existed before full worker began.
        outcome_count=0;site_count=0;ranked=0
        for p in sorted((folder/'outcomes').glob('*.json')):
            event=x.load(p)
            if event['attempt']>rec['offspring_completed']:continue
            outcome_count+=1;site_count+=len(event['variants'])
            assert event['operator']==x.schedule_operator(np,g,rec['seed'],event['attempt'])
            assert len(event['variants'])<=3
            for trial in event['variants']:
                payload=g.payload(g.dec(trial['tree']))
                assert payload['execution_key']==trial['execution_key'] and g.limits(payload)==trial['structure_error']
            if event['selected_trial'] is not None:
                chosen=next(r for r in event['variants'] if r['trial_index']==event['selected_trial']);assert chosen['structure_legal']
                result=event['evaluation']
                if result.get('worker_started_perf') is not None:assert result['worker_started_perf']>=event['decision_saved_perf']
                if result.get('valid'):
                    assert len(result['instances'])==5 and result['worker_finished_perf']<launch['deadline']
                    assert result['mean_bins']==float(np.mean([r['bins_used'] for r in result['instances']]))
            if event['eligible_position_mechanism']:
                for trial in event['variants']:assert trial['target_path'] and trial['type']=='V'
                legal=[r for r in event['variants'] if r['structure_legal']]
                if len(legal)>=2:
                    ranked+=1
                    if rec['method']!='uniform_position_gp':
                        model=x.load(ROOT/'frozen'/('frozen_behavior_A_ranker.json' if rec['method']=='behavior_A_position_gp' else 'frozen_structure_ranker.json'))['model']
                        vocab=x.load(ROOT/'frozen/operator_vocabulary.json')
                        for trial in legal:assert x.rank_score(np,model,trial,vocab)==trial['rank_score']
                        best=sorted(legal,key=lambda r:(-r['rank_score'],x.tie(r)))[0];assert best['trial_index']==event['selected_trial']
                    else:assert g.choice(legal,g.rng(rec['seed'],event['attempt'],10))['trial_index']==event['selected_trial']
        assert outcome_count==rec['offspring_completed']
        for path in (folder/'worker_stderr').glob('*.bin'):
            if b'PermissionError' in path.read_bytes():all_io.append(path.relative_to(ROOT).as_posix())
        assert not (folder/'stderr.log').read_bytes(),'Run controller error'
        audit_rows.append({'seed':rec['seed'],'method':rec['method'],'commits':len(commits),'completed_offspring':outcome_count,'completed_trial_sites':site_count,'completed_ranked_proposals':ranked,'deadline_verified':True})
    assert len(init)==len(cfg['search_seeds'])
    test=x.load(ROOT/'test_complete.json');assert test['nominal_instance_results']==(cfg['runs']+3)*30
    assert test['results_sha256']==x.sha(ROOT/'test_instance_results.csv')
    assert x.load(ROOT/'test_nonoverlap_audit.json')['passed']
    for rel,h in x.load(ROOT/'test_inputs_lock.json')['files'].items():assert x.sha(ROOT/rel)==h
    extra=[]
    assert x.load(ROOT/'test_data_reuse_audit.json')['passed']
    result={'at':x.now(),'passed':not all_io,'research_runs':cfg['runs'],'paired_initial_populations_exact':True,'all_deadline_commits_verified':True,
        'all_selected_children_chosen_before_full_labels':True,'all_completed_structure_checks_replayed':True,
        'frozen_ranking_scores_and_selected_sites_verified':True,'main_run_IO_worker_failures':all_io,
        'reused_test_instance_results':test['nominal_instance_results'],'reused_data_bytes_identical':True,'original_test_nonoverlap_audit_retained':True,'frozen_sources_unchanged':True,'models_retrained':False,'new_LLM_calls':0,
        'user_requested_20seed_extension':True,'failed_startup_archives':extra,'run_audits':audit_rows,'audit_wall_seconds':time.perf_counter()-start,
        'tail_note':'Counters labelled committed exclude work interrupted before a commit. Entire120s is charged regardless; partial/tail worker files separately retained. No late child recovered into population.'}
    x.save(ROOT/'completion_audit.json',result)
    accounting={'search':{'nominal_run_seconds':cfg['nominal_total_search_seconds'],'measured_scheduler_stop_seconds':sum(r['scheduler_stop_elapsed'] for r in summary),'scheduler_full_batch_wall_seconds':out['search_wall_seconds'],
        'cleanup_seconds':sum(r['cleanup_seconds'] for r in summary),'budget_includes':'startup/imports/assets/initialization/proposals/probes/inference/full fitness/selection/logs; cold per run'},
        'failed_startups':[],
        'failed_startup_cost_note':'This extension has no automatic retries. Original startup costs remain in the untouched prior cohort; any extension infrastructure fault stops the pipeline.',
        'test_data_preparation':x.load(ROOT/'test_preparation_cost.json'),'fixed_output_testing':test,
        'upstream_cost_note':'Historical LLM, extraction and ranker training are pre-existing costs, not zero. Their prior archives remain references; no new model requests or training in this experiment.',
        'new_LLM_calls':0,'audit_wall_seconds':result['audit_wall_seconds']}
    x.save(ROOT/'cost_accounting.json',accounting)
    with (ROOT/'REPORT.md').open('a',encoding='utf-8') as f:
        f.write('\n## 擴充範圍與完整性\n\n本批次為使用者新增20個配對種子的要求，沿用原演算法、凍結模型、120秒上限與同一已查看測試集。原10種子封存不修改，新增20與合併30分開呈現；不將種子擴充解讀為新的盲測。沒有自動補抽或重啟。\n\n')
        f.write('逐 run 的初始化、截止提交、選位先於完整品質、凍結排序分數及共用測試資料雜湊已稽核。' if result['passed'] else '完整性稽核有未通過項目，須先查看 `completion_audit.json`，不能宣稱為乾淨確認。')
        f.write('\n\n逐段計數只涵蓋已提交工作；截止當下若中斷在探針或寫檔中，最後部分的細分時間／計數可能不完整，但全部實際搜尋時間仍收費，未恢復中斷子代作收益。\n')
    # Seal produced artifacts after audit. Exclude live pipeline status/log files.
    x.save(ROOT/'progress.json',{'status':'complete' if result['passed'] else 'complete_with_audit_failure','completed_runs':cfg['runs'],'test_complete':True,'at':x.now(),'report':'REPORT.md'})
    excluded={'manifest.json','pipeline_status.json','pipeline_stdout.log','pipeline_stderr.log'}
    files={p.relative_to(ROOT).as_posix():x.sha(p) for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and 'pipeline_logs' not in p.parts and p.name not in excluded and not p.name.endswith('.tmp')}
    x.save(ROOT/'manifest.json',{'at':x.now(),'files':files,'new_LLM_calls':0,'completed_runs':cfg['runs'],'audit_passed':result['passed']})
    print(json.dumps({'completion_audit_passed':result['passed'],'runs':cfg['runs'],'test_results':test['nominal_instance_results'],'manifest_files':len(files)}),flush=True)

if __name__=='__main__':main()
