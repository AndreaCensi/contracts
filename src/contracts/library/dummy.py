#cython: language_level=3, annotation_typing=True, c_string_encoding=utf-8, boundscheck=False, wraparound=False, initializedcheck=False
from ..interface import Contract, ContractNotRespected
from ..syntax import add_contract, W, Literal


class Any(Contract):
    """ Always true. """

    def __init__(self, where=None):
        Contract.__init__(self, where)

    def __repr__(self):
        return 'Any()'

    def __str__(self):
        return '*'

    def check_contract(self, context, value, silent):
        pass

    @staticmethod
    def parse_action(s, loc, tokens):  # @UnusedVariable
        return Any(W(s, loc))


class Never(Contract):
    """ A contract that does not match anything. Useful for debugging. """

    def __init__(self, where=None):
        Contract.__init__(self, where)

    def __repr__(self):
        return 'Never()'

    def __str__(self):
        return '#'

    def check_contract(self, context, value, silent):
        raise ContractNotRespected(self, 'No value can match this',
                                   value, context)

    @staticmethod
    def parse_action(s, loc, tokens):  # @UnusedVariable
        return Never(W(s, loc))


add_contract(Literal('*').setParseAction(Any.parse_action))
add_contract(Literal('#').setParseAction(Never.parse_action))
