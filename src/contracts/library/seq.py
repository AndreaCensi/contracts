#cython: language_level=3, annotation_typing=True, c_string_encoding=utf-8, boundscheck=False, wraparound=False, initializedcheck=False
from ..interface import Contract, ContractNotRespected
from ..syntax import (add_contract, W, contract_expression, O, S, add_keyword,
    Keyword)
import collections.abc as collections
from past.builtins import xrange

try:
    import numpy
    has_numpy = True
except ImportError:
    has_numpy = False


class Seq(Contract):

    def __init__(self, length_contract=None,
                    elements_contract=None, where=None):
        Contract.__init__(self, where)
        self.length_contract = length_contract
        self.elements_contract = elements_contract

    def check_contract(self, context, value, silent):
        if has_numpy and isinstance(value, numpy.ndarray):
            # use value.size and value.flat for iteration
            if self.length_contract is not None:
                self.length_contract._check_contract(context, value.size, silent)

            if self.elements_contract is not None:
                n = value.size
                for i in xrange(n):
                    element = value.flat[i]
                    if ((element.dtype == numpy.int32) or
                        (element.dtype == numpy.int64)):
                        element = int(element)
                    # XXX: hack
                    self.elements_contract._check_contract(context, element, silent)

            return

        if not isinstance(value, collections.Sequence):
            error = 'Expected a Sequence, got %r.' % value.__class__.__name__
            raise ContractNotRespected(self, error, value, context)

        if self.length_contract is not None:
            self.length_contract._check_contract(context, len(value), silent)

        if self.elements_contract is not None:
            for element in value:
                self.elements_contract._check_contract(context, element, silent)

    def __str__(self):
        s = 'seq'
        if self.length_contract is not None:
            s += '[%s]' % self.length_contract
        if self.elements_contract is not None:
            s += '(%s)' % self.elements_contract
        return s

    def __repr__(self):
        s = 'Seq(%r,%r)' % (self.length_contract, self.elements_contract)
        return s

    @staticmethod
    def parse_action(s, loc, tokens):
        where = W(s, loc)
        length_contract = tokens.get('length_contract', None)
        elements_contract = tokens.get('elements_contract', None)
        return Seq(length_contract, elements_contract, where=where)


list_contract = (Keyword('seq') -
                 O(S('[') - contract_expression('length_contract') - S(']')) +
                 O(S('(') - contract_expression('elements_contract') - S(')')))
list_contract.setParseAction(Seq.parse_action)

list_contract.setName('Seq contract')
add_keyword('seq')
add_contract(list_contract)
