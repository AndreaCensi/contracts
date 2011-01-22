from ..interface import Contract, ContractNotRespected
from ..syntax import add_contract, W, contract_expression, O, add_keyword, Keyword

class String(Contract):
    
    def __init__(self, length=None, where=None):
        Contract.__init__(self, where)
        self.length = length
        assert length is None or isinstance(length, Contract)
        
    def check_contract(self, context, value): 
        if not isinstance(value, str):
            error = 'Expected a string, got %r.' % value.__class__.__name__
            raise ContractNotRespected(contract=self, error=error,
                                       value=value, context=context)
       
        if self.length is not None:
            self.length._check_contract(context, len(value))
            
    def __repr__(self):
        return 'String(%r)' % self.length
    
    def __str__(self):
        s = 'str'
        if self.length is not None:
            s += '[%s]' % self.length
        return s
            
    @staticmethod
    def parse_action(s, loc, tokens): 
        where = W(s, loc)
        length = tokens.get('length', None)
        return String(length, where=where)
 

string_contract = (Keyword('str') | Keyword('string')) + \
                  O('[' - contract_expression('length') - ']') 
add_keyword('str')
add_keyword('string')

add_contract(string_contract.setParseAction(String.parse_action))
