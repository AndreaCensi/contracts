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

good('dict', {})
syntax_fail('dict[]')
syntax_fail('dict[]()')
syntax_fail('dict()')
good('dict[1]', {1:2})
good('dict[N],N<2', {1:2})
fail('dict[N],N<2', {1:2, 3:4})
good('dict(int:int)', {1:2})
fail('dict(int:int)', {'a':2})
good('dict(*:int)', {1:2})
good('dict(*:int)', {'a':2})

# dictionary of string -> tuple, with tuple of two elements with different type
good('dict(str:tuple)', {'a':(2, 1.1)})
good('dict(str:tuple(type(x),type(y))),x!=y', {'a':(2, 1.1)})
fail('dict(str:tuple(type(x),type(y))),x!=y', {'a':(2, 1)})


## dictionary of string -> tuple, with tuple of two elements with different type
## In this case, each value should have the same two types
#good('dict(str:tuple(type(x),type(y)),x!=y', {'a':(2, 1.1)})
#fail('dict(str:tuple(type(x),type(y)),x!=y', {'a':(2, 1)})
#
## This fails because we have x=int,y=float followed by float,int
#fail('dict(str:tuple(type(x),type(y)),x!=y', {'a':(2, 1.1), 'b': (1.1, 2)})
#
## Here we force the context to not match using $(...) 
#good('dict(str:$(tuple(type(x),type(y)),x!=y))', {'a':(2, 1.1), 'b': (1.1, 2)})
#fail('dict(str:$(tuple(type(x),type(y)),x!=y))', {'a':(2, 1)})



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

