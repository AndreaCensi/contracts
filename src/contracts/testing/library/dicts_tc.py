from .  import syntax_fail, good, fail

good('dict', {})
fail('dict', 1)
fail('dict', [])
syntax_fail('dict[]')
syntax_fail('dict[]()')
syntax_fail('dict()')
good('dict[1]', {1: 2})
good('dict[N],N<2', {1: 2})
fail('dict[N],N<2', {1: 2, 3: 4})
good('dict(int:int)', {1: 2})
fail('dict(int:int)', {'a': 2})
good('dict(*:int)', {1: 2})
good('dict(*:int)', {'a': 2})

# dictionary of string -> tuple, with tuple of two elements with different type
good('dict(str:tuple(type(x),type(y))),x!=y', {'a': (2, 1.1)})
fail('dict(str:tuple(type(x),type(y))),x!=y', {'a': (2, 1)})
