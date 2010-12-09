
class ContractException(Exception):
    pass

#class Where:
#    ''' Represents a position in the stream. '''
    

class ParsingError(ContractException):
    ''' Raised when we couldn't parse an expression. '''
    def __init__(self, error, where):
        self.error = error
        self.where = where

    def __str__(self):
        return self.error
    
class ContractNotRespected(Exception):
    
    def __init__(self, contract, error, value, expected, context):
        self.contract = contract
        self.error = error
        self.value = value
        self.expected = expected
        self.context = context
        
    def __str__(self):
        return self.error

def check_contracts(contracts, values):
    ''' 
        Checks that the values respect the contract. 
        
        :param contracts: List of contracts.
        :type contracts:  list(N,str),N>0
        
        :param values: Values that should match the contracts.
        :type values: list(N)
    
        :return: True if everything matches.
        :rtype: bool
        
        :raise: ContractError
    '''
    pass


def add_contract_type(ctype):
    pass

class Context:
    ''' Class that represents the context for checking an expression. '''
    
    def __init__(self):
        self.variables = {}
        
    def add_variable(self, name, desc, origin, value):
        pass

class Contract:
    
    def __init__(self, expression):
        pass
    
    def check_contract(self, context, value):
        ''' 
            Checks that value is ok with this contract in the specific 
            context. 
        '''
        pass
    
    
    def get_syntax(self):
        ''' Returns the pyparsing syntax that matches this contract. '''
    
        pass
    
    
    
    
    
    
    
