from contracts import check_contracts, ContractException
from contracts.interface import ContractNotRespected
from contracts.main import parse_contract_string

def check_contract_ok(contract, value):
    check_contracts([contract], [value])
            
def check_contract_fail(contract, value):
    try:
        context = check_contracts([contract], [value])
        
        msg = ('I was expecting that %r would not satisfy %r.\n' % 
               (value, contract))
        parsed_contract = parse_contract_string(contract)
        msg += ' contract:         %s\n' % parsed_contract
        msg += ' matched context:  %s\n' % context
        raise Exception(msg)
    except ContractNotRespected as e:
        pass
