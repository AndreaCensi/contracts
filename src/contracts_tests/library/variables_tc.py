from contracts.test_registrar import fail, good, syntax_fail, semantic_fail

# only single letters
syntax_fail("NN")
syntax_fail("xx")

# big letters can only bind to numbers
good("N,N>0", 1)
fail("N,N>0", 0)
semantic_fail("N", [])

# lower case can bind to anything
good("x", 1)
good("x", [])
