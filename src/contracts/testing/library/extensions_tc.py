from contracts import new_contract
from contracts.test_registrar import fail, good, syntax_fail



@new_contract
def ext0_positive(value):
    return value > 0

@new_contract
def ext1_lessthan(value, threshold):
    return value < threshold


good('ext0_positive', 1)
fail('ext0_positive', -1)


good('ext1_lessthan(0)', -1)  
fail('ext1_lessthan(0)', +1)
# named
good('ext1_lessthan(threshold=0)', -1)  
fail('ext1_lessthan(threshold=0)', +1)


# needs to fail parsing because we didn't provide argument
syntax_fail('ext1_lessthan')
# needs to fail parsing because the argument name is wrong
syntax_fail('ext1_lessthan(th=0)')
# too many arguments
syntax_fail('ext1_lessthan(0,1)')

