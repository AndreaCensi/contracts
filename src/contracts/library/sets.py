from ..interface import Contract, ContractNotRespected, describe_type
from ..syntax import (Keyword, O, S, W, add_contract, add_keyword, 
    contract_expression)


class ASet(Contract):

    def __init__(self, length_contract=None,
                 elements_contract=None, where=None):
        Contract.__init__(self, where)
        self.length_contract = length_contract
        self.elements_contract = elements_contract

    def check_contract(self, context, value, silent):
        if not isinstance(value, set):
            error = 'Expected a set, got %r.' % describe_type(value)
            raise ContractNotRespected(self, error, value, context)

        if self.length_contract is not None:
            self.length_contract._check_contract(context, len(value), silent)

        if self.elements_contract is not None:
            for element in value:
                self.elements_contract._check_contract(context, element, silent)

    def __str__(self):
        s = 'set'
        if self.length_contract is not None:
            s += '[%s]' % self.length_contract
        if self.elements_contract is not None:
            s += '(%s)' % self.elements_contract
        return s

    def __repr__(self):
        s = 'ASet(%r,%r)' % (self.length_contract, self.elements_contract)
        return s

    @staticmethod
    def parse_action(s, loc, tokens):
        where = W(s, loc)
        length_contract = tokens.get('length_contract', None)
        elements_contract = tokens.get('elements_contract', None)
        return ASet(length_contract, elements_contract, where=where)


list_contract = (Keyword('set') - 
                 O(S('[') - contract_expression('length_contract') - S(']')) + 
                 O(S('(') - contract_expression('elements_contract') - S(')')))
list_contract.setParseAction(ASet.parse_action)

list_contract.setName('Set contract')
add_keyword('set')
add_contract(list_contract)
