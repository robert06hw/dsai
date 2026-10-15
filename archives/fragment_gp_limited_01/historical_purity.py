"""Pure ordered-tree normalization and three equivalent score representations."""
import ast,copy
import numpy as np
import scoring as sc

MAX_EXPANDED_NODES=256
MAX_PROGRAM_CHARACTERS=2000

def _none(node): return isinstance(node,ast.Constant) and node.value is None

def check_purity(tree):
    for node in ast.walk(tree):
        if not isinstance(node,ast.Call): continue
        for kw in node.keywords:
            if kw.arg is None: raise ValueError('Expanded keyword arguments outside pure representation DSL')
            if kw.arg=='out' and not _none(kw.value): raise ValueError('Mutating out argument outside pure representation DSL')
            if kw.arg=='overwrite_input' and not (isinstance(kw.value,ast.Constant) and not kw.value.value):
                raise ValueError('overwrite_input outside pure representation DSL')
        if isinstance(node.func,ast.Attribute) and isinstance(node.func.value,ast.Name) and node.func.value.id=='np':
            name=node.func.attr;obj=getattr(np,name,None)
            if isinstance(obj,np.ufunc):
                if len(node.args)>obj.nin and not _none(node.args[obj.nin]): raise ValueError('Positional mutating out argument')
            out_index={'sum':3,'mean':3,'std':3,'min':2,'max':2,'median':2,'percentile':3,'quantile':3,'stack':2,'clip':3,'argmin':2,'argmax':2}.get(name)
            if out_index is not None and len(node.args)>out_index and not _none(node.args[out_index]):
                raise ValueError('Positional mutating out argument')
            overwrite_index={'median':3,'percentile':4,'quantile':4}.get(name)
            if overwrite_index is not None and len(node.args)>overwrite_index:
                value=node.args[overwrite_index]
                if not (isinstance(value,ast.Constant) and not value.value): raise ValueError('Positional overwrite_input')
        if isinstance(node.func,ast.Attribute) and node.func.attr in {'reduce','accumulate'} and len(node.args)>3 and not _none(node.args[3]):
            raise ValueError('Positional ufunc-method mutating out argument')

def expanded_expression(code):
    sc.compile_score(code)
    tree=ast.parse(code);check_purity(tree)
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef));env={}
    class Expand(ast.NodeTransformer):
        def visit_Name(self,node): return copy.deepcopy(env[node.id]) if node.id in env else node
    for statement in fn.body:
        if isinstance(statement,ast.Expr): continue
        value=Expand().visit(copy.deepcopy(statement.value))
        if sum(1 for _ in ast.walk(value))>MAX_EXPANDED_NODES: raise ValueError('Expanded ordered-tree complexity cap')
        if isinstance(statement,ast.Assign): env[statement.targets[0].id]=value
        elif isinstance(statement,ast.Return): return value
    raise ValueError('Missing return')

def canonical(code): return ast.dump(expanded_expression(code),include_attributes=False)

def representations(node):
    result={'expression':'def score(item, bins):\n    return '+ast.unparse(node)+'\n'}
    for rep in sc.REPS[1:]:
        lines=[];cache={}
        def name_for(n,number):
            if rep=='temporary': return f'v{number}'
            if isinstance(n,ast.BinOp) and ast.unparse(n)=='bins - item': return 'residual'
            if isinstance(n,ast.BinOp) and isinstance(n.op,ast.Mult): return f'product_{number}'
            if isinstance(n,ast.BinOp) and isinstance(n.op,ast.Div): return f'normalized_penalty_{number}'
            if isinstance(n,ast.UnaryOp): return f'negative_penalty_{number}'
            if isinstance(n,ast.BinOp) and isinstance(n.op,ast.Sub): return f'target_distance_{number}'
            if isinstance(n,ast.Compare): return f'feasible_mask_{number}'
            if isinstance(n,ast.IfExp): return f'conditional_score_{number}'
            if isinstance(n,ast.Subscript): return f'selected_values_{number}'
            if isinstance(n,ast.Attribute): return f'array_{n.attr}_{number}'
            if isinstance(n,ast.Call):
                call=ast.unparse(n.func).split('.')[-1]
                return f'{call}_value_{number}'
            return f'adjustment_{number}'
        def walk(n,materialize=True):
            if isinstance(n,(ast.Name,ast.Constant)): return ast.unparse(n)
            # Dtypes, constants and NumPy function objects retain their spelling.
            if isinstance(n,ast.Attribute) and isinstance(n.value,ast.Name) and n.value.id=='np': return ast.unparse(n)
            key=ast.dump(n,include_attributes=False)
            if key in cache and materialize: return cache[key]
            if isinstance(n,(ast.IfExp,ast.Compare)):
                # Preserve short-circuit/lazy evaluation inside the expression.
                rhs=ast.unparse(n)
            else:
                built=copy.deepcopy(n)
                for field,value in ast.iter_fields(built):
                    if field in {'ctx','op','ops'}: continue
                    if isinstance(value,ast.expr):
                        if isinstance(n,ast.Call) and field=='func':
                            if isinstance(value,ast.Attribute) and not (isinstance(value.value,ast.Name) and value.value.id=='np'):
                                value.value=ast.parse(walk(value.value),mode='eval').body
                            setattr(built,field,value)
                        else: setattr(built,field,ast.parse(walk(value),mode='eval').body)
                    elif isinstance(value,ast.Slice):
                        for bound in ['lower','upper','step']:
                            v=getattr(value,bound)
                            if v is not None: setattr(value,bound,ast.parse(walk(v),mode='eval').body)
                    elif isinstance(value,list):
                        changed=[]
                        for v in value:
                            if isinstance(v,ast.expr): v=ast.parse(walk(v),mode='eval').body
                            elif isinstance(v,ast.keyword): v.value=ast.parse(walk(v.value),mode='eval').body
                            changed.append(v)
                        setattr(built,field,changed)
                rhs=ast.unparse(built)
            if not materialize or isinstance(n,(ast.List,ast.Tuple)): return rhs
            # Match the previous arithmetic formatter's explicit parentheses.
            if isinstance(n,ast.BinOp): rhs='('+rhs+')'
            elif isinstance(n,ast.UnaryOp) and isinstance(n.op,ast.USub):
                child=walk(n.operand);rhs=f'-({child})'
            number=len(lines)+1;name=name_for(n,number);lines.append(f'    {name} = {rhs}');cache[key]=name
            return name
        returned=walk(node)
        if not lines:
            returned='v1' if rep=='temporary' else 'bin_scores';lines.append(f'    {returned} = {ast.unparse(node)}')
        result[rep]='def score(item, bins):\n'+'\n'.join(lines)+f'\n    return {returned}\n'
    return result

def make(code,initial=None):
    node=expanded_expression(code);tree=ast.dump(node,include_attributes=False);key=sc.sha(tree)
    programs=initial if initial is not None else representations(node)
    if any(len(p)>MAX_PROGRAM_CHARACTERS for p in programs.values()): raise ValueError('Common representation length cap')
    if any(canonical(p)!=tree for p in programs.values()): raise AssertionError('Representation changed ordered tree')
    return {'key':key,'canonical_ast':tree,'programs':programs,'expanded_nodes':sum(1 for _ in ast.walk(node))}
