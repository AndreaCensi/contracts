from contracts.test_registrar import good, fail


good('0', 0)
good('1', 1)
fail('1', 2)
