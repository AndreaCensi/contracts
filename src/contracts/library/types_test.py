from contracts.test_registrar import syntax_fail, good, fail


good('int', 1)
fail('int', None)
fail('int', 2.0)
good('float', 1.1)
fail('float', None)
fail('float', 2)
