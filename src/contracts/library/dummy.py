from contracts.interface import Contract
from contracts.syntax import add_contract, W, Literal


class DummyContract(Contract):
    ''' Always true. '''

    def __repr__(self):
        return '*'
    
    def check_contract(self, context, value):
        pass
    
    @staticmethod
    def parse_action(s, loc, tokens): #@UnusedVariable
        return DummyContract(W(s, loc))


add_contract(Literal('*').setParseAction(DummyContract.parse_action))
