from .  import syntax_fail, good, fail


good('map', {})
fail('map', 1)
fail('map', [])
syntax_fail('map[]')
syntax_fail('map[]()')
syntax_fail('map()')
good('map[1]', {1: 2})
good('map[N],N<2', {1: 2})
fail('map[N],N<2', {1: 2, 3: 4})
good('map(int:int)', {1: 2})
fail('map(int:int)', {'a': 2})
good('map(*:int)', {1: 2})
good('map(*:int)', {'a': 2})

# mapionary of string -> tuple, with tuple of two elements with different type
good('map(str:tuple(type(x),type(y))),x!=y', {'a': (2, 1.1)})
fail('map(str:tuple(type(x),type(y))),x!=y', {'a': (2, 1)})
