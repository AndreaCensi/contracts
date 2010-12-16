from pyparsing import oneOf
from contracts.interface import Contract, ContractNotRespected, \
    ContractSemanticError
from contracts.syntax import W, add_contract

class BindVariable(Contract):
    
    def __init__(self, where, variable, allowed_types):
        assert isinstance(variable, str) and len(variable) == 1
        Contract.__init__(self, where)
        self.variable = variable
        self.allowed_types = allowed_types
    
    def check_contract(self, context, value):
        if context.has_variable(self.variable):
            expected = context.set_variable(self.variable)
            if not (expected == value):
                # TODO: add where it was bound
                error = ('Expected that %r = %r, got %r.' % 
                         (self.variable, expected, value))
                raise ContractNotRespected(contract=self, error=error,
                                           value=value, context=context)
            
        else:
            # bound variable
            if not isinstance(value, self.allowed_types):
                error = ('Variable %r can only bind to %r, not %r.' % 
                         (self.variable, self.allowed_types,
                          value.__class__.__name__))
                raise ContractSemanticError(self, error, context)
            
            context.set_variable(self.variable, value, origin=self)
            
    def __repr__(self):
        return self.variable
        
    @staticmethod
    def parse_action(allowed_types):
        def parse(s, loc, tokens):
            where = W(s, loc)
            variable = tokens[0]
            return BindVariable(where, variable, allowed_types)
        return parse


variables = oneOf('A B C D E F G H I J K L M N O P Q R S T U W V X Y Z')

variables.setParseAction(BindVariable.parse_action(int))

add_contract(variables)
