#cython: language_level=3, annotation_typing=True, c_string_encoding=utf-8, boundscheck=False, wraparound=False, initializedcheck=False
from ..interface import Contract, ContractNotRespected
from ..syntax import W, contract_expression, add_contract, add_keyword, Keyword
from Aspidites._vendor.pyparsing import (Dict, delimitedList, Group, alphanums, Suppress, Literal,
    Word)


class Attr(Contract):
    def __init__(self, attrs, where=None):
        # attrs: dict(str: contract)
        Contract.__init__(self, where)
        if not attrs:
            raise ValueError('Need some attributes') 
        self.attrs = attrs

    def check_contract(self, context, value, silent):
        for k in self.attrs:
            if hasattr(value, k):
                self.attrs[k]._check_contract(context, getattr(value, k), silent)
            else:
                error = 'Expected an attribute %r.' % k
                raise ContractNotRespected(contract=self, error=error,
                                           value=value, context=context)


    def __str__(self):
        sattrs = ";".join(['%s:%s' % (k, self.attrs[k]) for k in sorted(self.attrs)]) 
        return 'attr(%s)' % sattrs

    def __repr__(self):
        rattrs = ",".join(['%r:%r' % (k, self.attrs[k]) for k in sorted(self.attrs)]) 
        return 'Attr({%s})' % rattrs

    @staticmethod
    def parse_action(s, loc, tokens):
        where = W(s, loc)
        attrs = tokens.get('attrs', None)
        # Python 3 only
        # attrs = {k: v for k, v in attrs.items()}
        attrs = dict([(k, v) for k, v in attrs.items()])
        return Attr(attrs, where=where)

attr_spec = Dict(
        delimitedList(
            Group(Word(alphanums) + 
                    Suppress(Literal(':')) + 
                    contract_expression('value')),
            delim=';')
        )('attrs')
attrs_spec = ('(' - attr_spec - ')')


attr_contract = Keyword('attr') - attrs_spec
attr_contract.setParseAction(Attr.parse_action)

add_contract(attr_contract)
add_keyword('attr')
