"""Conservative NumPy expression trees: S/V numbers and BS/BV masks."""
import ast, copy, hashlib, json, math

NUM={'S','V'}; BOOL={'BS','BV'}
UNARY={'abs','absolute','sqrt','square','log','log1p','log2','exp','expm1','tanh','sin','cos','floor','ceil','round','sign','negative'}
BINARY={'minimum','maximum','multiply','divide','subtract','power'}
REDUCE={'mean','sum','min','max','std','median','prod','argmin','argmax'}

def key(node):return hashlib.sha256(ast.dump(node,include_attributes=False).encode()).hexdigest()
def parse(text):return ast.parse(text,mode='eval').body
def text(node):return ast.unparse(node)
def promote(types,boolean=False):
    allowed=BOOL if boolean else NUM
    if not types or any(t not in allowed for t in types):raise ValueError('Incompatible operand types: '+str(types))
    vector=any(t in {'V','BV'} for t in types)
    return ('BV' if vector else 'BS') if boolean else ('V' if vector else 'S')
def function_name(n):
    if isinstance(n,ast.Name):return n.id
    if isinstance(n,ast.Attribute):return function_name(n.value)+'.'+n.attr
    raise ValueError('Unsupported callable')

def infer(n):
    if isinstance(n,ast.Name):
        if n.id=='item':return 'S'
        if n.id=='bins':return 'V'
        raise ValueError('Unexpanded local '+n.id)
    if isinstance(n,ast.Constant):
        if isinstance(n.value,bool):return 'BS'
        if isinstance(n.value,(int,float)):return 'S'
        raise ValueError('Non-numeric terminal')
    if isinstance(n,ast.Attribute):
        name=function_name(n)
        if name in {'np.pi','np.e','np.inf','np.nan','bins.size','bins.ndim'}:return 'S'
        raise ValueError('Unsupported expression attribute '+name)
    if isinstance(n,ast.BinOp):
        if isinstance(n.op,(ast.BitAnd,ast.BitOr)):return promote([infer(n.left),infer(n.right)],True)
        if isinstance(n.op,(ast.Add,ast.Sub,ast.Mult,ast.Div,ast.FloorDiv,ast.Pow,ast.Mod)):
            return promote([infer(n.left),infer(n.right)])
        raise ValueError('Unsupported binary operator')
    if isinstance(n,ast.UnaryOp):
        t=infer(n.operand)
        if isinstance(n.op,ast.Invert):
            if t!='BV':raise ValueError('Invert requires vector mask; scalar Python bool has numeric invert semantics')
            return t
        if isinstance(n.op,(ast.USub,ast.UAdd)) and t in NUM:return t
        raise ValueError('Incompatible unary operator')
    if isinstance(n,ast.Compare):
        if len(n.ops)!=1 or len(n.comparators)!=1:raise ValueError('Chained comparison excluded')
        t=promote([infer(n.left),infer(n.comparators[0])]);return 'BV' if t=='V' else 'BS'
    if isinstance(n,ast.IfExp):
        if infer(n.test)!='BS' or infer(n.body)!=infer(n.orelse):raise ValueError('Conditional branch shape not guaranteed')
        return infer(n.body)
    if isinstance(n,ast.Subscript):
        if function_name(n.value)=='bins.shape' if isinstance(n.value,ast.Attribute) else False:
            if isinstance(n.slice,ast.Constant) and n.slice.value==0:return 'S'
        if infer(n.value)!='V':raise ValueError('Subscript requires vector')
        index=n.slice
        if isinstance(index,ast.Constant) and isinstance(index.value,int) and not isinstance(index.value,bool):return 'S'
        if isinstance(index,ast.UnaryOp) and isinstance(index.op,ast.USub) and isinstance(index.operand,ast.Constant) and isinstance(index.operand.value,int):return 'S'
        if isinstance(index,ast.Slice) and index.lower is None and index.upper is None:
            if index.step is None:return 'V'
            if ast.literal_eval(index.step) in [-1,1]:return 'V'
        raise ValueError('Variable/ragged indexing excluded')
    if isinstance(n,ast.Call):
        name=function_name(n.func);args=[infer(a) for a in n.args]
        for kw in n.keywords:
            if kw.arg=='dtype' and function_name(kw.value)=='np.float64':continue
            if kw.arg=='axis' and isinstance(kw.value,ast.Constant) and kw.value.value is None:continue
            raise ValueError('Unsupported keyword or shape option')
        if name.startswith('np.'):
            f=name[3:]
            if f in UNARY and len(args)==1:return promote(args)
            if f in BINARY and len(args)==2:return promote(args)
            if f in REDUCE and args==['V']:return 'S'
            if f in {'any','all'} and len(args)==1 and args[0] in NUM|BOOL:return 'BS'
            if f=='logical_and' and len(args)==2:return promote(args,True)
            if f=='where' and len(args)==3 and args[0] in BOOL:
                out=promote(args[1:]);return 'V' if args[0]=='BV' or out=='V' else 'S'
            if f=='clip' and len(args)==3:return promote(args)
            if f in {'zeros_like','ones_like'} and len(args)==1 and args[0] in NUM:return args[0]
            if f=='full_like' and len(args)==2 and args[0] in NUM and args[1]=='S':return args[0]
            if f in {'asarray','array'} and len(args)==1 and args[0] in NUM:return args[0]
            if f in {'percentile','quantile'} and args==['V','S']:return 'S'
            if f in {'maximum.reduce','minimum.reduce'} and args==['V']:return 'S'
            if f in {'maximum.accumulate','minimum.accumulate'} and args==['V']:return 'V'
        if name in {'abs','float','int','round'} and len(args)==1:
            if name=='abs':return promote(args)
            if args==['S']:return 'S'
        if name=='len' and args==['V']:return 'S'
        if name in {'min','max'} and len(args)>=1 and set(args)=={'S'}:return 'S'
        raise ValueError('Unsupported call/type signature '+name+str(args))
    raise ValueError('Unsupported expression node '+type(n).__name__)

def child_fields(n):
    """Only replace actual expression operands, never call names/shape metadata."""
    if isinstance(n,ast.Attribute) and isinstance(n.value,ast.Name) and n.value.id=='np':return
    if isinstance(n,ast.Subscript) and isinstance(n.value,ast.Attribute) and function_name(n.value)=='bins.shape':return
    for field,value in ast.iter_fields(n):
        if field in {'func','slice'}:continue
        if isinstance(value,ast.expr):yield (field,None),value
        elif isinstance(value,list):
            for i,v in enumerate(value):
                if isinstance(v,ast.expr):yield (field,i),v

def locations(n,path=()):
    yield path,n,infer(n)
    for component,child in child_fields(n):yield from locations(child,path+(component,))
def size(n):return sum(1 for _ in locations(n))
def depth(n):return 1+max((depth(c) for _,c in child_fields(n)),default=0)
def replace(n,path,new):
    out=copy.deepcopy(n)
    if not path:return copy.deepcopy(new)
    p=out
    for field,index in path[:-1]:p=getattr(p,field) if index is None else getattr(p,field)[index]
    field,index=path[-1]
    if index is None:setattr(p,field,copy.deepcopy(new))
    else:getattr(p,field)[index]=copy.deepcopy(new)
    return out

def canonical(n):
    """No reassociation, commutative sorting or behavioral merging."""
    n=copy.deepcopy(n)
    for component,c in list(child_fields(n)):
        f,i=component
        if i is None:setattr(n,f,canonical(c))
        else:getattr(n,f)[i]=canonical(c)
    if isinstance(n,ast.UnaryOp) and isinstance(n.op,ast.UAdd) and infer(n.operand) in NUM:return n.operand
    if isinstance(n,ast.UnaryOp) and isinstance(n.op,ast.USub):
        if isinstance(n.operand,ast.Constant) and isinstance(n.operand.value,(int,float)) and not isinstance(n.operand.value,bool):
            return ast.Constant(value=-n.operand.value)
        if isinstance(n.operand,ast.UnaryOp) and isinstance(n.operand.op,ast.USub):return n.operand.operand
    return n

def expand_program(code,max_nodes=4096,max_depth=64):
    module=ast.parse(code);functions=[s for s in module.body if isinstance(s,ast.FunctionDef)]
    if len(functions)!=1 or functions[0].name!='score':raise ValueError('One score function required')
    env={};dependencies=[];returned=None
    class Inline(ast.NodeTransformer):
        def visit_Name(self,n):
            if n.id in env:return copy.deepcopy(env[n.id])
            if n.id in {'bins','item','np','abs','min','max','float','int','len','round'}:return copy.deepcopy(n)
            raise ValueError('Unresolved dependency '+n.id)
    for s in functions[0].body:
        if isinstance(s,ast.Expr) and isinstance(s.value,ast.Constant) and isinstance(s.value.value,str):continue
        if isinstance(s,ast.Assign) and len(s.targets)==1 and isinstance(s.targets[0],ast.Name):
            names=sorted({n.id for n in ast.walk(s.value) if isinstance(n,ast.Name) and isinstance(n.ctx,ast.Load)})
            value=Inline().visit(copy.deepcopy(s.value));infer(value)
            if size(value)>max_nodes or depth(value)>max_depth:raise ValueError('Expansion safety limit exceeded')
            env[s.targets[0].id]=value
            dependencies.append({'local':s.targets[0].id,'line':s.lineno,'direct_dependencies':names,
                'expanded_expression':text(value),'expanded_key':key(value),'type':infer(value)})
        elif isinstance(s,ast.Return):returned=Inline().visit(copy.deepcopy(s.value));break
        else:raise ValueError('Not straight-line local assignments and return')
    if returned is None:raise ValueError('No return')
    if infer(returned)!='V':raise ValueError('Return not guaranteed a numeric bin-score vector')
    if size(returned)>max_nodes or depth(returned)>max_depth:raise ValueError('Expansion safety limit exceeded')
    return returned,dependencies

def program(n):return 'def score(item, bins):\n    return '+text(n)+'\n'
def call(name,*args):return ast.Call(func=parse('np.'+name),args=list(args),keywords=[])
def binary(op,a,b):return ast.BinOp(left=a,op=op,right=b)
def terminal(t,rng,safe=False):
    if t=='S':
        if not safe and rng.random()<.1:return parse(['np.pi','np.e','np.inf','np.nan','bins.size','bins.ndim','bins.shape[0]'][int(rng.integers(7))])
        return parse('item') if rng.random()<.4 else ast.Constant(value=float(rng.choice([-100,-50,-25,-20,-10,-5,-1,0,1,5,10,20,25,50,100])))
    if t=='V':
        choices=['bins','bins - item','-bins','np.zeros_like(bins)','np.ones_like(bins)']
        return parse(choices[int(rng.integers(len(choices)))])
    return parse('item > 0') if t=='BS' else parse('bins > item')

def random_tree(t,rng,levels=3,safe=False):
    if levels<=1 or rng.random()<.25:return terminal(t,rng,safe)
    child=lambda x:random_tree(x,rng,levels-1,safe)
    if t in BOOL:
        numeric='V' if t=='BV' else 'S'
        op=int(rng.integers(5))
        if op==0:return ast.UnaryOp(op=ast.Invert(),operand=child(t)) if t=='BV' else ast.Compare(left=child('S'),ops=[ast.Gt()],comparators=[child('S')])
        if op==1:return binary(ast.BitAnd(),child(t),child(t))
        if op==2:return binary(ast.BitOr(),child(t),child(t))
        if op==3:return call('logical_and',child(t),child(t))
        return ast.Compare(left=child(numeric),ops=[rng.choice([ast.Lt(),ast.Gt(),ast.LtE(),ast.GtE()])],comparators=[child('S')])
    shape=lambda: 'V' if t=='V' and rng.random()<.65 else 'S'
    ops=['add','sub','mul','safe_div','minimum','maximum','abs','square','where']
    if not safe:ops+=['div','pow','floor_div','power','mod','sqrt','log','log1p','log2','exp','expm1','tanh','sin','cos','floor','ceil','round','sign','clip','multiply','divide','subtract','negative','absolute','zeros_like','ones_like','full_like','asarray','array','ifexp']
    if t=='V' and not safe:ops+=['maximum.accumulate','minimum.accumulate','reverse']
    if t=='S' and not safe:ops+=sorted(REDUCE)+['percentile','quantile','len','float','int','builtin_abs','builtin_round','builtin_min','builtin_max','maximum.reduce','minimum.reduce','index']
    op=ops[int(rng.integers(len(ops)))]
    if op in REDUCE and t=='S':return call(op,child('V'))
    if op=='len':return ast.Call(func=ast.Name(id='len',ctx=ast.Load()),args=[child('V')],keywords=[])
    if op in {'float','int','builtin_abs','builtin_round','builtin_min','builtin_max'}:
        name=op.replace('builtin_','');args=[child('S')]
        if name in {'min','max'}:args.append(child('S'))
        return ast.Call(func=ast.Name(id=name,ctx=ast.Load()),args=args,keywords=[])
    if op in {'maximum.reduce','minimum.reduce','maximum.accumulate','minimum.accumulate'}:return call(op,child('V'))
    if op=='index':return ast.Subscript(value=child('V'),slice=ast.Constant(value=0),ctx=ast.Load())
    if op=='reverse':return ast.Subscript(value=child('V'),slice=ast.Slice(lower=None,upper=None,step=ast.UnaryOp(op=ast.USub(),operand=ast.Constant(value=1))),ctx=ast.Load())
    if op=='ifexp':return ast.IfExp(test=child('BS'),body=child(t),orelse=child(t))
    if op in {'asarray','array','zeros_like','ones_like'}:return call(op,child(t))
    if op=='full_like':return call(op,child(t),child('S'))
    if op in {'percentile','quantile'}:return call(op,child('V'),ast.Constant(value=50. if op=='percentile' else .5))
    if op=='where':return call('where',child('BV' if t=='V' else 'BS'),child(t),child('S'))
    if op in UNARY:return call(op,child(t))
    if op=='clip':return call('clip',child(t),ast.Constant(value=-100.),ast.Constant(value=100.))
    a=child(t);b=child(shape())
    if op=='safe_div':return binary(ast.Div(),a,call('maximum',call('abs',b),ast.Constant(value=1.)))
    if op in BINARY:return call(op,a,b)
    operators={'add':ast.Add,'sub':ast.Sub,'mul':ast.Mult,'div':ast.Div,'mod':ast.Mod,'pow':ast.Pow,'floor_div':ast.FloorDiv}
    return binary(operators[op](),a,b)

def tests():
    n,d=expand_program('def score(item,bins):\n a=bins-item\n b=a*a\n return -b\n')
    assert infer(n)=='V' and len(d)==2 and d[1]['direct_dependencies']==['a']
    assert key(canonical(parse('-(-bins)')))==key(parse('bins'))
    assert infer(parse('np.where(bins>item, -bins, 0)'))=='V'
    assert infer(parse('np.mean(bins)'))=='S'
    for bad in ['bins[bins>item]','np.stack([bins,bins])','bins & item']:
        try:infer(parse(bad))
        except ValueError:continue
        raise AssertionError('Expected incompatible/unknown shape')
    z=replace(n,(),parse('-bins'));assert key(z)==key(parse('-bins'))
    return {'dependency_expansion':True,'four_type_shape_rules':True,'no_ragged_mask_indexing':True,
        'conservative_normalization':True,'typed_subtree_replacement':True}
