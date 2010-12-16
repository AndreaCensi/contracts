from contracts import check_contracts
from contracts.interface import ContractNotRespected, ContractSemanticError
from contracts.main import parse_contract_string

def check_contract_single_ok(contract, value):
    check_contracts([contract], [value])
            
def check_contract_single_fail(contract, value):
    try:
        context = check_contracts([contract], [value])
        
        msg = ('I was expecting that %r would not satisfy %r.\n' % 
               (value, contract))
        parsed_contract = parse_contract_string(contract)
        msg += ' contract:         %s\n' % parsed_contract
        msg += ' matched context:  %s\n' % context
        raise Exception(msg)
    
    except (ContractNotRespected, ContractSemanticError) as e:
        pass



def check_contracts_ok(contracts, values):
    check_contracts(contracts, values)
            
def check_contracts_fail(contracts, values):
    try:
        context = check_contracts(contracts, values)
        
        msg = ('I was expecting that %r would not satisfy %r.\n' % 
               (values, contracts))
#        parsed_contract = parse_contract_string(contract)
#        msg += ' contract:         %s\n' % parsed_contract
#        msg += ' matched context:  %s\n' % context
        raise Exception(msg)
    
    except (ContractNotRespected, ContractSemanticError) as e:
        pass
