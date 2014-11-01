from . import syntax_fail, good, fail

syntax_fail('=1+')
syntax_fail('=1-')
syntax_fail('=1*')

for number in [1, 1.0, 1e10, -1]:
    good('=%r' % number, number)
    good('%r' % number, number)

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
good(['N', 'Y,N==Y+1'], [5, 4])

# Checking precedence
good('1+2*3', 7)
good('2*3+1', 7)
# Now with parentheses
good('=1+1*3', 4)
good('=(1+1)*3', 6)

good('1+1+1', 3)
good('2*2*2', 8)
good('2-1-1', 0)

# Wrong math
fail('x,x+1=0', 'ciao')
fail('x,-x=0', 'ciao')

# Binding to non-existing variable
fail('N+1=0', 1)


