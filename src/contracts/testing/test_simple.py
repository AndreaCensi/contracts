
from .utils import ContractTestCase

# list(N,tuple(str, value))
good_examples = []
fail_examples = []
def good_example(a, b): good_examples.append((a, b))
def fail_example(a, b): fail_examples.append((a, b))

good_example('list', [])
fail_example('list', 'ciao')
good_example('list(1)', [0])
good_example('list(2)', [0, 1])
fail_example('list(2)', [0])
good_example('list(int)', [])
good_example('list(int)', [0, 1])
fail_example('list(int)', [0, 'a'])
fail_example('list(int)', [0, 'a'])
good_example('list(int, >0)', [2, 1])
fail_example('list(int, >0)', [0, 1])

# with parametric lengths 
good_example('list(N)', [])
good_example('list(N),N>0', [1])
fail_example('list(N),N>0', [])


''' 

Syntax for lists:

    list( element_spec, element_spec, ... )
    list( size, element_spec, element_spec, ... )
    
    size: integer or variables

'''
 
class SimpleTests(ContractTestCase):
       
    def test_simple_expressions_ok(self):
        for contract, value in good_examples:
            self.check_contract_ok(contract, value)

    def test_simple_expressions_fail(self):
        for contract, value in good_examples:
            self.check_contract_fail(contract, value)
