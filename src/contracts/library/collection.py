import collections

from ..interface import Contract, ContractNotRespected
from ..syntax import (add_contract, W, contract_expression, O, S, add_keyword,
    Keyword)


class Collection(Contract):

    def __init__(self, length_contract=None,
                    elements_contract=None, where=None):
        Contract.__init__(self, where)
        self.length_contract = length_contract
        self.elements_contract = elements_contract

        try:
            # latest python 3.6+
            self.__collection_types = collections.abc.Collection
        except:
            try:
                # older python 3
                self.__collection_types = collections.Collection
            except:
                # python 2
                self.__collection_types = (collections.Sequence, collections.Set, collections.Mapping, collections.deque,)

    def check_contract(self, context, value, silent):
        if not isinstance(value, self.__collection_types):
            error = 'Expected a Collection, got %r.' % value.__class__.__name__
            raise ContractNotRespected(self, error, value, context)

        if self.length_contract is not None:
            self.length_contract._check_contract(context, len(value), silent)

        if self.elements_contract is not None:
            for element in value:
                self.elements_contract._check_contract(context, element, silent)

    def __str__(self):
        s = 'collection'
        if self.length_contract is not None:
            s += '[%s]' % self.length_contract
        if self.elements_contract is not None:
            s += '(%s)' % self.elements_contract
        return s

    def __repr__(self):
        return 'Collection({0!r},{0!r})'.format(self.length_contract, self.elements_contract)

    @staticmethod
    def parse_action(s, loc, tokens):
        where = W(s, loc)
        length_contract = tokens.get('length_contract', None)
        elements_contract = tokens.get('elements_contract', None)
        return Collection(length_contract, elements_contract, where=where)


list_contract = (Keyword('collection') -
                 O(S('[') - contract_expression('length_contract') - S(']')) +
                 O(S('(') - contract_expression('elements_contract') - S(')')))
list_contract.setParseAction(Collection.parse_action)

list_contract.setName('Collection contract')
add_keyword('collection')
add_contract(list_contract)
