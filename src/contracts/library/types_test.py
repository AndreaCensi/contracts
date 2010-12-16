from contracts.test_registrar import syntax_fail, good, fail, semantic_fail


good('int', 1)
fail('int', None)
fail('int', 2.0)
good('float', 1.1)
fail('float', None)
fail('float', 2)

syntax_fail('type')
syntax_fail('type()')
good('type(x)', 1)
semantic_fail('type(X)', 1)
