from contracts.test_registrar import syntax_fail, good, fail


syntax_fail('=1+')
syntax_fail('=1-')
syntax_fail('=1*')

good('=2', 2)
good('=1+1', 2)
good('1+1', 2)
good('=1-1', 0)
good('1-1', 0)

good(['N', 'N-1'], [1, 0])
good(['N', 'N+1'], [1, 2])

good(['N', 'N-1'], [1, 0])
good(['N', 'N*4'], [1, 4])
good(['N', 'Y, N == Y + 1'], [5, 4])

