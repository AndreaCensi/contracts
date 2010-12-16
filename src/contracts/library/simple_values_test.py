from contracts.test_registrar import syntax_fail, good, fail


good('0', 0)
good('1', 1)
fail('1', 2)
