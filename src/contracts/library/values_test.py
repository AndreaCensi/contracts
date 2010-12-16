from contracts.test_registrar import syntax_fail, good, fail, semantic_fail

# Basic comparisons
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

# wrong types
good('=1', 1)
semantic_fail('=1', [1])
semantic_fail('=0', [0])

semantic_fail('>0', [])
