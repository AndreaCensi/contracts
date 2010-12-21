from contracts import check_contracts
from ..interface import ContractSyntaxError
from ..main import parse_contract_string

def check_contracts_ok(contract, value):
    if isinstance(contract, str):
        contract = [contract]
        value = [value]
    check_contracts(contract, value)
            
def check_contracts_fail(contract, value, error):
    if isinstance(contract, str):
        contract = [contract]
        value = [value]
        
    try:
        context = check_contracts(contract, value)
        
        msg = ('I was expecting that %r would not satisfy %r.\n' % 
               (value, contract))
        msg += ' matched context:  %s\n' % context
        for c in contract:
            parsed_contract = parse_contract_string(c)
            msg += ' contract:     %20s  %r\n' % (parsed_contract, parsed_contract)
        raise Exception(msg)
    
    except error as e:
        pass

def check_syntax_fail(string):
    assert isinstance(string, str)
    
    try:
        parsed_contract = parse_contract_string(string)
        msg = 'I would not expect to parse %r.' % string
        msg += ' contract:         %s\n' % parsed_contract
        raise Exception(msg)
    
    except ContractSyntaxError:
        pass
    
