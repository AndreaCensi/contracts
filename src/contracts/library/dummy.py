from contracts.interface import Contract
from contracts.syntax import add_contract, W, Literal


class Any(Contract):
    ''' Always true. '''

    def __repr__(self):
        return 'Any()'

    def __str__(self):
        return '*'
    
    def check_contract(self, context, value):
        pass
    
    @staticmethod
    def parse_action(s, loc, tokens): #@UnusedVariable
        return Any(W(s, loc))


add_contract(Literal('*').setParseAction(Any.parse_action))
