from contracts.interface import Contract, ContractNotRespected
from contracts.syntax import W, add_contract, contract, S
from pyparsing import Literal

class CheckType(Contract):
    def __init__(self, where, types):
        Contract.__init__(self, where)
        self.types = types
    
    def check_contract(self, context, value):
        if not isinstance(value, self.types):
            error = 'Expected type %r, got %r.' % (self.types.__name__,
                                                   value.__class__.__name__)
            raise ContractNotRespected(contract=self, error=error,
                                       value=value, context=context)
    
    def __repr__(self):
        return self.types.__name__

    @staticmethod
    def parse_action(types):
        return lambda s, loc, tokens: CheckType(W(s, loc), types) #@UnusedVariable

add_contract(Literal('int').setParseAction(CheckType.parse_action(int)))

add_contract(Literal('float').setParseAction(CheckType.parse_action(float)))



class Type(Contract):
    def __init__(self, where, type_constraint):
        Contract.__init__(self, where)
        self.type_constraint = type_constraint
        
    def check_contract(self, context, value):
        val = context.eval(value)
        self.type_constraint.check_contract(context, type(value))
    
    def __repr__(self):
        return 'type(%r)' % self.type_constraint

    @staticmethod
    def parse_action(s, loc, tokens):
        type_constraint = tokens['type_constraint']
        return Type(W(s, loc), type_constraint) #@UnusedVariable


type_contract = S('type') + S('(') + contract('type_constraint') + S(')')

add_contract(type_contract.setParseAction(Type.parse_action))



