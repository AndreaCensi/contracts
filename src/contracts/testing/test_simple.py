import traceback

from ..main import parse_contract_string 
from ..interface import ContractSemanticError, ContractNotRespected, VariableRef
from ..test_registrar import (good_examples, semantic_fail_examples,
                              syntax_fail_examples, contract_fail_examples)
from .utils import check_contracts_ok, check_syntax_fail, check_contracts_fail

from . import test_multiple #@UnusedImport

# TODO: remove all of these
from contracts.syntax import EqualTo

# Import all the symbols needed to eval() the __repr__() output.
from contracts.library import *

select = False
#select = True
if select:
    good_examples[:] = []
    syntax_fail_examples[:] = []
    semantic_fail_examples[:] = []
    contract_fail_examples[:] = []
    from ..test_registrar import  fail, good, syntax_fail, semantic_fail

    good('#|*,(#|*)', None)
    
    good('1+2*(3+4)', 15)
    good('1+1*(2+2)', 5)
    good('1*(1+2+2)', 5)
    
    good('1+1+1', 3)
    good('2*2*2', 8)
    good('2-1-1', 0)

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

# Checks that we can eval() the __repr__() value and we get an equivalent object. 
def test_repr():
    for contract, value in (good_examples + semantic_fail_examples): #@UnusedVariable
        if isinstance(contract, list):
            for c in contract:
                yield check_good_repr, c
        else:
            yield check_good_repr, contract

#  Checks that we can reconvert the __str__() value and we get the same. 
def test_reconversion():
    for contract, value in (good_examples + semantic_fail_examples): #@UnusedVariable
        if isinstance(contract, list):
            for c in contract:
                yield check_recoversion, c
        else:
            yield check_recoversion, contract
        
def check_good_repr(c):
    ''' Checks that we can eval() the __repr__() value and we get
        an equivalent object. '''
    parsed = parse_contract_string(c)
    
    # Check that it compares true with itself
    assert parsed.__eq__(parsed), 'Repr does not know itself: %r' % parsed
    
    repr = parsed.__repr__()
    
    try:
        reeval = eval(repr)
    except Exception as e:
        traceback.print_exc()
        raise Exception('Could not evaluate expression %r: %s' % (repr, e))
        
    assert reeval == parsed, 'Repr gives different object:\n  %r !=\n  %r' % (parsed, reeval)
    
def check_recoversion(s):
    ''' Checks that we can eval() the __repr__() value and we get
        an equivalent object. '''
    parsed = parse_contract_string(s)
    s2 = parsed.__str__()
    reconv = parse_contract_string(s2)
    
    msg = 'Reparsing gives different objects:\n'
    msg += '  Original string: %r\n' % s
    msg += '           parsed: %r\n' % parsed
    msg += '      Regenerated: %r\n' % s2
    msg += '         reparsed: %r' % reconv
    
    assert reconv == parsed, msg
    
    # warn if the string is not exactly the same
    
    if s2 != s: 
        print('Slight different regenerated strings:')
        print('   original: %s' % s)
        print('  generated: %s' % s2)
        print('   parsed the first time as: %r' % parsed)
        print('                and then as: %r' % reconv)
