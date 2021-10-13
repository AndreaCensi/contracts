#cython: language_level=3, annotation_typing=True, c_string_encoding=utf-8, boundscheck=False, wraparound=False, initializedcheck=False

from ..interface import Contract, ContractNotRespected
from ..syntax import (W, contract_expression, O, S, add_contract, add_keyword,
    Keyword)


class Dict(Contract):

    def __init__(self, length=None, key_c=None, value_c=None, where=None):
        Contract.__init__(self, where)
        self.length = length
        self.key_c = key_c
        self.value_c = value_c

    def check_contract(self, context, value, silent):
        if not isinstance(value, dict):
            error = 'Expected a dict, got %r.' % value.__class__.__name__
            raise ContractNotRespected(contract=self, error=error,
                                       value=value, context=context)

        if self.length is not None:
            self.length._check_contract(context, len(value), silent)

        for k in value:
            if self.key_c is not None:
                self.key_c._check_contract(context, k, silent)
            if self.value_c is not None:
                self.value_c._check_contract(context, value[k], silent)

    def __str__(self):
        s = 'dict'
        if self.length is not None:
            s += '[%s]' % self.length
        if self.key_c is not None:
            k = str(self.key_c)
        else:
            k = ''
        if self.value_c is not None:
            v = str(self.value_c)
        else:
            v = ''
        if k or v:
            s += '(%s:%s)' % (k, v)
        return s

    def __repr__(self):
        return 'Dict(%r,%r,%r)' % (self.length, self.key_c, self.value_c)

    @staticmethod
    def parse_action(s, loc, tokens):
        where = W(s, loc)
        length = tokens.get('length', None)
        key = tokens.get('key', None)
        value = tokens.get('value', None)
        return Dict(length, key, value, where=where)


length_spec = S('[') - contract_expression('length') - S(']')
kv_spec = ('(' - O(contract_expression('key'))
           + ':' + O(contract_expression('value')) - ')')
dict_contract = Keyword('dict') + O(length_spec) + O(kv_spec)

dict_contract.setParseAction(Dict.parse_action)

add_contract(dict_contract)
add_keyword('dict')
