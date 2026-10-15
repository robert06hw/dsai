"""Independently random syntax, conditioned only on type/node-count/depth."""
import ast,collections,hashlib,json,sys,time,warnings
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'fragment_gp_limited_30seed_extension_01'
sys.path.insert(0,str(SOURCE))
import typed_tree as t
def save(name,x):
    p=ROOT/name;p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def maximum(d):return (3**d-1)//2
def possible(kind,n,d):
    if kind in ['S','V']:return d>=1 and d<=n<=maximum(d)
    return d>=2 and d+1<=n<=1+2*maximum(d-1)
def allocation(total,k,d,r):
    forced=int(r.integers(k));lo=[1]*k;lo[forced]=d
    assert sum(lo)<=total<=k*maximum(d)
    order=list(r.permutation(k));sizes=[0]*k;remaining=total
    for pos,j in enumerate(order):
        rest=order[pos+1:];low=max(lo[j],remaining-len(rest)*maximum(d));high=min(maximum(d),remaining-sum(lo[a] for a in rest))
        sizes[j]=int(r.integers(low,high+1));remaining-=sizes[j]
    assert remaining==0
    depths=[]
    for j,n in enumerate(sizes):
        if j==forced:depths.append(d)
        else:
            ds=[z for z in range(1,min(d,n)+1) if n<=maximum(z)];depths.append(int(r.choice(ds)))
    return sizes,depths
def generate(kind,n,d,r):
    assert possible(kind,n,d),(kind,n,d)
    if d==1:
        if kind=='V':return t.parse('bins')
        return t.parse('item') if r.random()<.3 else ast.Constant(value=float(r.uniform(0,100)))
    if kind=='BV':
        if possible('BV',n-1,d-1) and r.random()<.3:
            return ast.UnaryOp(op=ast.Invert(),operand=generate('BV',n-1,d-1,r))
        ns,ds=allocation(n-1,2,d-1,r);kinds=['V','S'];r.shuffle(kinds)
        if r.random()<.3:kinds=['V','V']
        a,b=[generate(k,s,z,r) for k,s,z in zip(kinds,ns,ds)]
        return ast.Compare(left=a,ops=[r.choice([ast.Lt(),ast.Gt(),ast.LtE(),ast.GtE(),ast.Eq(),ast.NotEq()])],comparators=[b])
    arities=[k for k in [1,2,3] if (d-1)+(k-1)<=n-1<=k*maximum(d-1)]
    k=int(r.choice(arities));ns,ds=allocation(n-1,k,d-1,r)
    kinds=['S']*k
    if kind=='V':
        kinds[int(r.integers(k))]='V'
        for j in range(k):
            if r.random()<.5:kinds[j]='V'
    children=[generate(q,s,z,r) for q,s,z in zip(kinds,ns,ds)]
    if k==1:
        op=str(r.choice(['abs','square','negative','tanh','sin','cos','floor','ceil','round','sign','unary_minus']))
        return ast.UnaryOp(op=ast.USub(),operand=children[0]) if op=='unary_minus' else t.call(op,*children)
    if k==3:return t.call('clip',*children)
    op=str(r.choice(['add','subtract','multiply','minimum','maximum']))
    if op in ['minimum','maximum']:return t.call(op,*children)
    return t.binary({'add':ast.Add,'subtract':ast.Sub,'multiply':ast.Mult}[op](),*children)
def probes(node,kind):
    # Interface-only tests; no packing, dataset quality, or behavior ranking.
    fn=eval(compile(ast.Expression(ast.fix_missing_locations(node)),'random-fragment','eval'),{'np':np,'item':1.,'bins':np.asarray([1.])})
    code=compile(ast.Expression(ast.fix_missing_locations(node)),'random-fragment','eval')
    for item in [1.,25.,50.,100.]:
        for bins in [np.asarray([item]),np.asarray([item,100.]),np.linspace(item,100.,13)]:
            with np.errstate(all='ignore'):
                out=np.asarray(eval(code,{'np':np,'item':item,'bins':bins.copy()}))
            assert np.isfinite(out).all()
            assert out.shape==(bins.shape if kind in ['V','BV'] else ())
            assert (np.issubdtype(out.dtype,np.bool_) if kind=='BV' else np.issubdtype(out.dtype,np.number))
def main():
    assert not (ROOT/'libraries/matched_random_fragments.json').exists(),'Bank already fixed'
    start=time.perf_counter();idx=load(SOURCE/'sources/historical_tree_index.json')
    raw={r['key']:r for r in load(SOURCE/'libraries/raw_fragments.json')}
    eligible=sorted([r for r in idx['fragment_eligibility'] if r['eligible']],key=lambda x:x['key'])
    assert len(eligible)==1240
    bank=[];seen=set();rejections=collections.Counter();attempts=0
    for slot,target in enumerate(eligible):
        rng=np.random.default_rng(np.random.SeedSequence([918273645,slot,901]))
        for local in range(10000):
            attempts+=1
            try:
                node=generate(target['type'],target['nodes'],target['depth'],rng)
                emitted=t.parse(t.text(node));key=t.key(emitted)
                assert (t.infer(emitted),t.size(emitted),t.depth(emitted))==(target['type'],target['nodes'],target['depth'])
                if key in seen:rejections['structural_duplicate']+=1;continue
                if t.key(t.canonical(emitted)) in idx['normalized']:rejections['full_historical_root']+=1;continue
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore');probes(emitted,target['type'])
            except Exception as exc:
                rejections[type(exc).__name__]+=1;continue
            break
        else:raise RuntimeError(f'Cannot match slot {slot}: {target}')
        seen.add(key);bank.append({'slot':slot,'template_key':target['key'],'key':key,'expression':t.text(emitted),'type':target['type'],'nodes':target['nodes'],'depth':target['depth'],
            'terminal_dependencies':sorted({x.id for x in ast.walk(emitted) if isinstance(x,ast.Name) and x.id in ['item','bins']}),
            'historical_fragment_AST_overlap':key in raw,'generation_attempts':local+1})
        if (slot+1)%200==0:print(f'Matched bank {slot+1}/1240',flush=True)
    save('libraries/matched_random_fragments.json',bank)
    hist=collections.Counter((r['type'],r['nodes'],r['depth']) for r in eligible)
    actual=collections.Counter((r['type'],r['nodes'],r['depth']) for r in bank);assert hist==actual
    save('bank_match_audit.json',{'passed':True,'bank_size':1240,'unique_ASTs':1240,'matching':'Exact per historical eligible sampling slot: output type, emitted nodes, emitted depth. Same per-type order via template keys.','historical_bank_size_raw':1947,'historical_eligible_size':1240,
        'exact_joint_distribution_match':True,'oversize_or_overdepth_fragments_each':sum(r['nodes']>64 or r['depth']>8 for r in bank),
        'full_historical_roots_excluded':True,'finite_shape_probes_per_fragment':12,'interface_probe_quality_selection':False,
        'historical_AST_overlaps':sum(r['historical_fragment_AST_overlap'] for r in bank),'forced_bin_terminal_overlap':'Vector one-node expression can only be bins under the unchanged grammar; overlap is recorded, not removed.',
        'bank_seed':918273645,'generator':'Independent random shape conditioned on type/size/depth, uniform feasible arities and allocations; not a shuffled or relabeled historical skeleton.',
        'operators':['add','subtract','multiply','minimum','maximum','clip','abs','square','negative','tanh','sin','cos','floor','ceil','round','sign','comparison','invert'],
        'constants':'nonnegative Uniform(0,100), signs via unary minus; preserves emitted node counting. Constant/operator frequencies and semantic difficulty are not matched.',
        'generation_attempts':attempts,'rejections':dict(rejections),'bank_build_wall_seconds':time.perf_counter()-start,'LLM_requests':0,'new_packing_evaluations':0})
    print(json.dumps(load(ROOT/'bank_match_audit.json'),ensure_ascii=False),flush=True)
if __name__=='__main__':main()
