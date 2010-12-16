from contracts.interface import Contract, ContractNotRespected
from contracts.syntax import W, add_contract
from pyparsing import Literal

class CheckType(Contract):
    
    def __init__(self, where, types):
        Contract.__init__(self, where)
        self.types = types
    
    def check_contract(self, context, value):
        val = context.eval(value)
        if not isinstance(val, self.types):
            error = 'Expected type %r, got %r.' % (str(self.types),
                                                   value.__class__.__name__)
            raise ContractNotRespected(
                    contract=self,
                    error=error,
                    value=value,
                    context=context)
    
    def __repr__(self):
        return self.types.__name__

    @staticmethod
    def parse_action(types):
        return lambda s, loc, tokens: CheckType(W(s, loc), types) #@UnusedVariable

add_contract(Literal('int').setParseAction(CheckType.parse_action(int)))

add_contract(Literal('float').setParseAction(CheckType.parse_action(float)))
