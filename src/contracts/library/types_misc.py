#cython: language_level=3, annotation_typing=True, c_string_encoding=utf-8, boundscheck=False, wraparound=False, initializedcheck=False
from ..interface import Contract, ContractNotRespected, describe_type
from ..syntax import (W, add_contract, contract_expression, S, Keyword,
    add_keyword)
from numbers import Number


class CheckType(Contract):

    def __init__(self, types, type_string=None, where=None):
        assert isinstance(types, type)
        Contract.__init__(self, where)
        self.types = types
        if type_string is None:
            self.type_string = types.__name__
        else:
            self.type_string = type_string

    def check_contract(self, context, value, silent):
        if not isinstance(value, self.types):
            error = 'Expected type %r, got %s.' % (self.types.__name__,
                                                   describe_type(value))
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
            return CheckType(types, tokens[0], where=where)  # @UnusedVariable
        return parse


add_contract(Keyword('Int').setParseAction(CheckType.parse_action(int)))
add_keyword('Int')

add_contract(Keyword('Float').setParseAction(CheckType.parse_action(float)))
add_keyword('Float')

add_contract(Keyword('Number').setParseAction(CheckType.parse_action(Number)))
add_keyword('Number')

add_contract(Keyword('bool').setParseAction(CheckType.parse_action(bool)))
add_keyword('bool')


class Type(Contract):
    def __init__(self, type_constraint, where=None):
        Contract.__init__(self, where)
        self.type_constraint = type_constraint

    def check_contract(self, context, value, silent):
        #  self.type_constraint._check_contract(context, type(value))
        self.type_constraint._check_contract(context, value.__class__, silent)

    def __str__(self):
        return 'type(%s)' % self.type_constraint

    def __repr__(self):
        return 'Type(%r)' % self.type_constraint

    @staticmethod
    def parse_action(s, loc, tokens):
        where = W(s, loc)
        type_constraint = tokens['type_constraint']
        return Type(type_constraint, where)


type_contract = (Keyword('type') - S('(')
                 - contract_expression('type_constraint') - S(')'))

add_contract(type_contract.setParseAction(Type.parse_action))
add_keyword('type')


