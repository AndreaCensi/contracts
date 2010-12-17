from contracts.main import parse_contract_string 
from contracts.interface import ContractSemanticError, ContractNotRespected
from contracts.testing.utils import check_contracts_ok, check_syntax_fail, \
    check_contracts_fail
from contracts.test_registrar import (good_examples, semantic_fail_examples,
                                      syntax_fail_examples, contract_fail_examples,
    fail, good, syntax_fail, semantic_fail)

from . import test_multiple #@UnusedImport

if True:
    good_examples[:] = []
    syntax_fail_examples[:] = []
    semantic_fail_examples[:] = []
    contract_fail_examples[:] = []



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

