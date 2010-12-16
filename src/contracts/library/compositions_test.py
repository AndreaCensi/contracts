from contracts.test_registrar import syntax_fail, good, fail

# AND
fail('=0,=1', 0)
good('=0,>=0', 0)

# OR
good('=0|=1', 0)
good('=0|=1', 1)
fail('=0|=1', 2)


good('0|1|2', 2)
good('0|1|2', 1)
good('list(0|1)', [0, 1, 0])
fail('list(0|1)', [0, 1, 2])
