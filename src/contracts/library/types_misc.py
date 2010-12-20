from contracts.interface import Contract, ContractNotRespected
from contracts.syntax import W, add_contract, contract, S
from pyparsing import Literal
import numbers
from types import NoneType

class CheckType(Contract):
    def __init__(self, types, type_string=None, where=None):
        Contract.__init__(self, where)
        self.types = types
        if type_string is None:
            self.type_string = types.__name__
        else:
            self.type_string = type_string
            
    def check_contract(self, context, value):
        if not isinstance(value, self.types):
            error = 'Expected type %r, got %r.' % (self.types.__name__,
                                                   value.__class__.__name__)
            raise ContractNotRespected(contract=self, error=error,
                                       value=value, context=context)
    
    def __str__(self):
        return self.type_string
    
    def __repr__(self):
        if self.types.__name__ == self.type_string:
            return 'CheckType(%s)' % (self.types.__name__)
        else:
            return 'CheckType(%s,%r)' % (self.types.__name__, self.type_string)
        
    @staticmethod
    def parse_action(types):
        def parse(s, loc, tokens):
            where = W(s, loc)
            return CheckType(types, tokens[0], where=where) #@UnusedVariable
        return parse

add_contract(Literal('int').setParseAction(CheckType.parse_action(int)))
add_contract(Literal('float').setParseAction(CheckType.parse_action(float)))
add_contract(Literal('bool').setParseAction(CheckType.parse_action(bool)))
add_contract(Literal('number').setParseAction(CheckType.parse_action(numbers.Number)))

add_contract(Literal('None').setParseAction(CheckType.parse_action(NoneType)))
add_contract(Literal('NoneType').setParseAction(CheckType.parse_action(NoneType)))


class Type(Contract):
    def __init__(self, type_constraint, where=None):
        Contract.__init__(self, where)
        self.type_constraint = type_constraint
        
    def check_contract(self, context, value): 
        self.type_constraint._check_contract(context, type(value))
    
    def __str__(self):
        return 'type(%s)' % self.type_constraint

    def __repr__(self):
        return 'Type(%r)' % self.type_constraint

    @staticmethod
    def parse_action(s, loc, tokens):
        where = W(s, loc)
        type_constraint = tokens['type_constraint']
        return Type(type_constraint, where) #@UnusedVariable


type_contract = S('type') + S('(') + contract('type_constraint') + S(')')

add_contract(type_contract.setParseAction(Type.parse_action))



