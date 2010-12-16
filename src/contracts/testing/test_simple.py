from contracts.testing.utils import check_contract_ok, check_contract_fail

#from .utils import ContractTestCase

# list(N,tuple(str, value))
good_examples = []
fail_examples = []
def good_example(a, b): good_examples.append((a, b))
def fail_example(a, b): fail_examples.append((a, b))


# Basic comparisons
good_example('=0', 0)
fail_example('=0', 1)
fail_example('=0', [0])
good_example('!=0', 1)
fail_example('!=0', 0)
good_example('>0', 1)
fail_example('>0', 0)
fail_example('>0', -1)
good_example('>=0', 1)
good_example('>=0', 0)
fail_example('>=0', -1)
good_example('<0', -1)
fail_example('<0', 0)
fail_example('<0', +1)
good_example('<=0', -1)
good_example('<=0', 0)
fail_example('<=0', +1)

# OR
good_example('=0|=1', 0)
good_example('=0|=1', 1)
fail_example('=0|=1', 2)


# TODO: error if N matches something except a number. x,y,z 

good_example('int', 1)
fail_example('int', None)
fail_example('int', 2.0)
good_example('float', 1.1)
fail_example('float', None)
fail_example('float', 2)


good_example('list', [])
fail_example('list', 'ciao')
good_example('=1', 1)
fail_example('=1', [1])
good_example('list[=1]', [0])
good_example('list[=2]', [0, 1])
fail_example('list[=2]', [0])
good_example('list[1]', [0]) # shortcut
good_example('list[2]', [0, 1])
fail_example('list[2]', [0])
good_example('list(int)', [])
good_example('list(int)', [0, 1])
fail_example('list(int)', [0, 'a'])
fail_example('list(int)', [0, 'a'])
good_example('list(int, >0)', [2, 1])
fail_example('list(int, >0)', [0, 1])
good_example('list(int, =0)', [0, 0])

# with parametric lengths 
good_example('list[N]', [])
good_example('list[N],N>0', [1])
good_example('list[N],N=1', [1])
fail_example('list[N],N>0', [])


''' 

Syntax for lists:

    list( element_spec, element_spec, ... )
    list( size, element_spec, element_spec, ... )
    
    size: integer or variables

'''
 
#class SimpleTests(ContractTestCase):
   
def test_simple_expressions_ok():
    for contract, value in good_examples:
        yield check_contract_ok, contract, value

def test_simple_expressions_fail():
    for contract, value in fail_examples:
        yield check_contract_fail, contract, value
