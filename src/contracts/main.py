from contracts.syntax import contract
from contracts.interface import Context, Contract, ContractSyntaxError
from pyparsing import ParseException
from procgraph.core.parsing_elements import Where

def check_contracts(contracts, values):
    ''' 
        Checks that the values respect the contract. 
        
        :param contracts: List of contracts.
        :type contracts:  list[N](str),N>0
        
        :param values: Values that should match the contracts.
        :type values: list[N]
    
        :return: a Context variable 
        :rtype: type(Context)
        
        :raise: ContractError
    '''
    assert len(contracts) == len(values)
    
    C = []
    for x in contracts:
        if not isinstance(x, str):
            raise ValueError('I expect arguments to be strings, not %r. ' % x)
        C.append(parse_contract_string(x))

    context = Context()
    for i in range(len(contracts)):
        C[i].check_contract(context, values[i])
    
    return context

def parse_contract_string(string, filename=None):
    try:
        c = contract.parseString(string, parseAll=True)[0] 
        assert isinstance(c, Contract), 'Want Contract, not %r' % c
        return c
    except ParseException as e:
        where = Where(filename, string, line=e.lineno, column=e.col)
        msg = 'Error in parsing string: %s' % e
        raise ContractSyntaxError(msg, where=where)
    
        

    
    

