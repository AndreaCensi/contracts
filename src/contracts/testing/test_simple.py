from contracts.main import parse_contract_string 
from contracts.interface import ContractSemanticError, ContractNotRespected
from contracts.testing.utils import check_contracts_ok, check_syntax_fail, \
    check_contracts_fail
from contracts.test_registrar import (good_examples, semantic_fail_examples,
                                      syntax_fail_examples, contract_fail_examples,
    fail, good, syntax_fail, semantic_fail)

from . import test_multiple #@UnusedImport

select = False
#select = True
if select:
    good_examples[:] = []
    syntax_fail_examples[:] = []
    semantic_fail_examples[:] = []
    contract_fail_examples[:] = []

good('-1<=1-1', None)

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
        if isinstance(contract, str):
            contract = [contract]
        
        for c in contract:
            parsed = parse_contract_string(c)
            if str(parsed) == c:
                mark = ' '
            else:
                mark = '~'
                
            print '{0} {1:>30} {2:>30} {3:>80}'.format(mark, c,
                                                       "%s" % parsed,
                                                      "%r" % parsed)


#def test_repr():
#    ''' Checks that we can eval() the __repr__() value and we get
#        an equivalent object. '''
#    for contract, value in (good_examples + semantic_fail_examples):
#        if isinstance(contract, list):
#            for c in contract:
#                yield check_good_repr, c
#        else:
#            yield check_good_repr, contract

def test_reconversion():
#    ''' Checks that we can reconvert the __str__() value and we get
#        the same. '''
    for contract, value in (good_examples + semantic_fail_examples):
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
    
    reeval = eval(repr)
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
        mark = '~'
        print('Slight different regenerated strings:')
        print('   original: %s' % s)
        print('  generated: %s' % s2)
        print('   parsed the first time as: %r' % parsed)
        print('                and then as: %r' % reconv)
