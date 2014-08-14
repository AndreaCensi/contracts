from . import good, fail, semantic_fail

# Basic comparisons, unitary syntax
good('=0', 0)
good('==0', 0)
fail('=0', 1)
fail('==0', 1)
good('!=0', 1)
fail('!=0', 0)
good('>0', 1)
fail('>0', 0)
fail('>0', -1)
good('>=0', 1)
good('>=0', 0)
fail('>=0', -1)
good('<0', -1)
fail('<0', 0)
fail('<0', +1)
good('<=0', -1)
good('<=0', 0)
fail('<=0', +1)

good('<=1', 1)
good('>=1', 1)
good('=1', 1)
good('<=1', 0)

# wrong types
good('=1', 1)
semantic_fail('=1', [1])
semantic_fail('=0', [0])

semantic_fail('>0', [])

# binary syntax
good('1>0', None)
fail('1>1', None)
good('0<1', None)
fail('1<1', None)
good('1>=0', None)
fail('1>=2', None)
good('0<=1', None)
fail('2<=1', None)
good('1=1', None)
fail('1=0', None)
good('1==1', None)
fail('1==0', None)
good('0!=1', None)
fail('0!=0', None)

good('1+1>=0', None)
fail('0>=1+1', None)
good('1-1=0', None)
fail('1-1=1', None)
good('-1<=1-1', None)
good('3*2>=2*1', None)

