from contracts.main import parse_contract_string 
from contracts.interface import ContractSemanticError, ContractNotRespected
from contracts.testing.utils import check_contracts_ok, check_syntax_fail, \
    check_contracts_fail
from contracts.test_registrar import (good_examples, semantic_fail_examples,
                                      syntax_fail_examples, contract_fail_examples,
    fail, good, syntax_fail, semantic_fail)

from . import test_multiple #@UnusedImport

if False:
    good_examples[:] = []
    syntax_fail_examples[:] = []
    semantic_fail_examples[:] = []
    contract_fail_examples[:] = []

from contracts.test_registrar import syntax_fail, good, fail

   
#### Tuples
good('tuple', ())
good('tuple', (1,))
# tuples and lists are different
fail('tuple', [])
fail('list', ())
# tuples can have the length
good('tuple[*]', (2, 2))
good('tuple[1]', (1,))
# you cannot specify every element
good('tuple(*)', (1,))
good('tuple(*,*)', (1, 2))
fail('tuple(*,*)', (1, 2, 3))
good('tuple(int,int)', (1, 2))
good('tuple(int,float)', (1, 2.0))
fail('tuple(float,float)', (1, 2.0))
good('tuple(type(x),type(x))', (1, 2))
# something complicated: nested tuples
good('tuple(x, tuple(*,*,x))', (1, (2, 3, 1)))
fail('tuple(x, tuple(*,*,x))', (1, (2, 3, 2)))
good('tuple(type(x), tuple(*,*,type(x)))', (1, (2.1, 3.0, 3)))
fail('tuple(type(x), tuple(*,*,type(x)))', (1, (2.1, 3.0, 3.1)))
# cannot specify both, even if coherent
syntax_fail('tuple[*](*,*)')
 


def test_good():
    for contract, value in good_examples:
        yield check_contracts_ok, contract, value

def test_syntax_fail():
    for s in syntax_fail_examples:
        yield check_syntax_fail, s
    
def test_semantic_fail():
    for contract, value in semantic_fail_examples:
        yield check_contracts_fail, contract, value, ContractSemanticError

def test_contract_fail():
    for contract, value in contract_fail_examples:
        yield check_contracts_fail, contract, value, ContractNotRespected

        
if False:
    for contract, value in (good_examples + semantic_fail_examples):
        parsed = parse_contract_string(contract)
        if str(parsed) == contract:
            mark = ' '
        else:
            mark = '~'
            
        print '{0:>20} {1:>20}  {2}'.format(contract, parsed, mark)

