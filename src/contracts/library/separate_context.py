from ..interface import Contract
from ..syntax import add_contract, W, contract, Literal

class SeparateContext(Contract):
    
    def __init__(self, where, contract):
        assert isinstance(contract, Contract)
        Contract.__init__(self, where)
        self.contract = contract
        
    def check_contract(self, context, value):
        copy = context.copy()
        self.contract.check_contract(copy, value)
    
    def __str__(self):
        return '$(%s)' % self.contract 
        
    def __repr__(self):
        return 'SeparateContext(%r)' % self.contract 
            
    @staticmethod
    def parse_action(s, loc, tokens):
        where = W(s, loc)
        return SeparateContext(where, tokens['child'])
 

sepcon = Literal('$') + Literal('(') + contract('child') + Literal(')')
sepcon.setParseAction(SeparateContext.parse_action)

add_contract(sepcon)
