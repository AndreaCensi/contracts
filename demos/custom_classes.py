from contracts import contract

class CustomClass(object):
    pass

@contract(x=CustomClass)
def f(x):
    pass


f(CustomClass()) # OK

f(42) # fails
#
# contracts.interface.ContractNotRespected: Breach for argument 'x' to f().
# Expected type 'CustomClass', got <type 'int'>.
# checking: CustomClass   for value: Instance of <type 'int'>: 42
