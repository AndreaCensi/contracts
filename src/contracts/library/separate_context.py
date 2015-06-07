from ..interface import Contract
from ..syntax import add_contract, W, contract_expression, Literal, Group


class SeparateContext(Contract):

    def __init__(self, contract, where=None):
        assert isinstance(contract, Contract)
        Contract.__init__(self, where)
        self.contract = contract

    def check_contract(self, context, value, silent):
        copy = context.copy()
        self.contract._check_contract(copy, value, silent)

    def __str__(self):
        return '$(%s)' % self.contract

    def __repr__(self):
        return 'SeparateContext(%r)' % self.contract

    @staticmethod
    def parse_action(s, loc, tokens):
        where = W(s, loc)
        return SeparateContext(tokens[0]['child'], where=where)


sepcon = (Group(Literal('$') + Literal('(') -
                contract_expression('child') - Literal(')')))
sepcon.setParseAction(SeparateContext.parse_action)
sepcon.setName('Context separation construct')
add_contract(sepcon)
