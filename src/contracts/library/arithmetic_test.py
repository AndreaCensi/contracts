from contracts.test_registrar import syntax_fail, good

syntax_fail('=1+')
syntax_fail('=1-')
syntax_fail('=1*')

good('=2', 2)
good('=1+1', 2)
good('1+1', 2)
good('=1-1', 0)
good('1-1', 0)

# unary operators

good('N,-N=-1', 1)

good(['N', 'N-1'], [1, 0])
good(['N', 'N+1'], [1, 2])

good(['N', 'N-1'], [1, 0])
good(['N', 'N*4'], [1, 4])
good(['N', 'Y, N == Y + 1'], [5, 4])

# Checking precedence
good('1+2*3', 7)
good('2*3+1', 7)
# Now with parentheses
good('=1+1*3', 4)
good('=(1+1)*3', 6)
