from contracts.interface import Contract, ContractNotRespected
from contracts.syntax import W

class CheckEqual(Contract):
    
    def __init__(self, where, expected):
        Contract.__init__(self, where)
        self.expected = expected
        
    def check_contract(self, context, value):
        if not(value == self.expected):
            error = ('Expected %r, got %r.' % (self.expected, value)) 
            
            raise ContractNotRespected(contract=self, error=error,
                                       value=value, context=context)
    
    def __repr__(self):
        return '%r' % self.expected
        
    @staticmethod
    def parse_action(s, loc, tokens):
        where = W(s, loc)
        value = tokens[0]
        return CheckEqual(where, value)
 
