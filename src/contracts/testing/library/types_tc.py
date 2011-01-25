from . import syntax_fail, good, fail, semantic_fail

# basic types

good('int', 1)
fail('int', None)
fail('int', 2.0)
good('float', 1.1)
fail('float', None)
fail('float', 2)

good('number', 1)
good('number', 1.0)
fail('number', [1])

good('bool', False)
good('bool', True)
fail('bool', 1)
fail('bool', 0)

# type contract

good('None', None)
good('NoneType', None)
fail('None', 1)
fail('NoneType', 1)

syntax_fail('type')
syntax_fail('type()')
good('type(x)', 1)
semantic_fail('type(X)', 1)
