from ..interface import Contract, ContractNotRespected
from ..syntax import (W, contract_expression, O, add_contract,
        add_keyword,
    Keyword)
from pyparsing import (Dict, delimitedList, Group, alphanums,
        Suppress, Literal, Word)


class Attr(Contract):
    def __init__(self, attrs=None, where=None):
        Contract.__init__(self, where)
        self.attrs = attrs

    def check_contract(self, context, value):
        # Everything is an object
        #if not isinstance(value, object):
        #    error = 'Expected an object, got %r.' % value.__class__.__name__
        #    raise ContractNotRespected(contract=self, error=error,
        #            value=value, context=context)

        if self.attrs is not None:
            for k in self.attrs:
                if hasattr(value, k):
                    self.attrs[k]._check_contract(context, getattr(value, k))

    def __str__(self):
        s = 'attr'
        if self.attrs is not None:
            for k in self.attrs:
                s += '(%s:%s),' % (k, self.attrs[k])
            if len(self.attrs.keys()):
                s = s[:-1]  # chop off last ','
        return s

    def __repr__(self):
        return 'Attr(%r)' % self.attrs

    @staticmethod
    def parse_action(s, loc, tokens):
        where = W(s, loc)
        attrs = tokens.get('attrs', None)
        if attrs is not None:
            # Python 3 only
            # attrs = {k: v for k, v in attrs.items()}
            attrs = dict([(k, v) for k, v in attrs.items()])
        return Attr(attrs, where=where)

attr_spec = Dict(
        delimitedList(
            Group(Word(alphanums) + \
                    Suppress(Literal(':')) + \
                    contract_expression('value')), \
            delim=';')
        )('attrs')
attrs_spec = ('(' - attr_spec - ')')


attr_contract = Keyword('attr') + O(attrs_spec)
attr_contract.setParseAction(Attr.parse_action)

add_contract(attr_contract)
add_keyword('attr')
