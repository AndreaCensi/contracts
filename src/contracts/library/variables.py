from pyparsing import oneOf
from contracts.interface import Contract, ContractNotRespected
from contracts.syntax import W, add_contract

class BindVariable(Contract):
    
    def __init__(self, where, variable):
        assert isinstance(variable, str) and len(variable) == 1
        Contract.__init__(self, where)
        self.variable = variable
    
    def check_contract(self, context, value):
        if context.has_variable(self.variable):
            expected = context.set_variable(self.variable)
            if not (expected == value):
                # TODO: add where it was bound
                error = ('Expected that %r = %r, got %r.' % 
                         (self.variable, expected, value))
                raise ContractNotRespected(
                    contract=self,
                    error=error,
                    value=value,
                    context=context)
            
        else:
            # bound variable
            context.set_variable(self.variable, value, origin=self)
            
    def __repr__(self):
        return self.variable
        
    @staticmethod
    def parse_action(s, loc, tokens):
        where = W(s, loc)
        variable = tokens[0]
        return BindVariable(where, variable)


variables = oneOf('A B C D E F G H I J K L M N O P Q R S T U W V X Y Z')

variables.setParseAction(BindVariable.parse_action)

add_contract(variables)
