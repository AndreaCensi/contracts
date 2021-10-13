#cython: language_level=3, annotation_typing=True, c_string_encoding=utf-8, boundscheck=False, wraparound=False, initializedcheck=False

import datetime

from ..interface import Contract, ContractNotRespected, describe_type
from ..syntax import Keyword, W, add_contract, add_keyword


class DatetimeWithTz(Contract):

    def __init__(self, length_contract=None,
                 elements_contract=None, where=None):
        Contract.__init__(self, where)
        self.length_contract = length_contract
        self.elements_contract = elements_contract

    def check_contract(self, context, value, silent):

        if not isinstance(value, datetime.datetime):
            error = 'Expected a datetime, got %r.' % describe_type(value)
            raise ContractNotRespected(self, error, value, context)

        if value.tzinfo is None:
            error = 'Expected a datetime with a timezone not a naive datetime '
            raise ContractNotRespected(self, error, value, context)

    def __str__(self):
        return 'datetime_tz'

    __repr__ = __str__

    @staticmethod
    def parse_action(s, loc, tokens):
        where = W(s, loc)
        return DatetimeWithTz(where=where)


list_contract = (Keyword('datetime_tz'))
list_contract.setParseAction(DatetimeWithTz.parse_action)

list_contract.setName('datetime_tz contract')
add_keyword('datetime_tz')
add_contract(list_contract)
