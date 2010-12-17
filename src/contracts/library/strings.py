from ..interface import Contract, ContractNotRespected
from ..syntax import add_contract, W, contract, O, S, OneOrMore

class String(Contract):
    
    def __init__(self, where, length=None):
        Contract.__init__(self, where)
        self.length = length
        assert length is None or isinstance(length, Contract)
        
    def check_contract(self, context, value): 
        if not isinstance(value, str):
            error = 'Expected a str, got %r.' % value.__class__.__name__
            raise ContractNotRespected(contract=self, error=error,
                                       value=value, context=context)
       
        if self.length is not None:
            self.length.check_contract(context, len(value))
            
    def __repr__(self):
        return 'String[%r]' % self.length
    
    def __str__(self):
        s = 'str'
        if self.length is not None:
            s += '[%s]' % self.length
        return s
            
    @staticmethod
    def parse_action(s, loc, tokens): 
        where = W(s, loc)
        if 'length' in tokens:
            length = tokens['length']
        else:
            length = None
            
        return String(where, length)
 

string_contract = 'str' + O('[' + contract('length') + ']') 

add_contract(string_contract.setParseAction(String.parse_action))
