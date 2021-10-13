#cython: language_level=3, annotation_typing=True, c_string_encoding=utf-8, boundscheck=False, wraparound=False, initializedcheck=False
from ..interface import Contract, ContractNotRespected
from ..syntax import(add_contract, W, contract_expression, O, S, ZeroOrMore,
                      Group, add_keyword, Keyword)
from .compositions import or_contract


class Tuple(Contract):

    def __init__(self, length=None, elements=None, where=None):
        Contract.__init__(self, where)
        self.length = length
        self.elements = elements
        assert elements is None or isinstance(elements, list)
        if elements:
            for e in elements:
                assert isinstance(e, Contract)

    def check_contract(self, context, value, silent):
        if not isinstance(value, tuple):
            error = 'Expected a tuple, got %r.' % value.__class__.__name__
            raise ContractNotRespected(contract=self, error=error,
                                       value=value, context=context)

        if self.length is not None:
            self.length._check_contract(context, len(value), silent)

        if self.elements is not None:
            if len(value) != len(self.elements):
                error = ('Expected a tuple of length '
                         '%s, got %r of length %s.' %
                         (len(self.elements), value, len(value)))
                raise ContractNotRespected(contract=self, error=error,
                                           value=value, context=context)

            for i in range(len(value)):
                self.elements[i]._check_contract(context, value[i], silent)

    def __repr__(self):
        return 'Tuple(%r,%r)' % (self.length, self.elements)

    def __str__(self):
        s = 'tuple'
        if self.length is not None:
            s += '[%s]' % self.length

        def rep(x):
            from .compositions import And
            if isinstance(x, And):
                return "(%s)" % x
            else:
                return "%s" % x

        if self.elements is not None:
            s += '(%s)' % ",".join(rep(x) for x in self.elements)
        return s

    @staticmethod
    def parse_action(s, loc, tokens):
        where = W(s, loc)
        length = tokens.get('length', [None])[0]
#        elements = tokens.get('elements', [None])[0]

        if 'elements' in tokens:
            elements = list(tokens['elements'])
        else:
            elements = None
        assert elements is None or length is None
        assert length is None or isinstance(length, Contract), ("Wrong type %r"
                                                                % length)

        if elements:
            for e in elements:
                assert isinstance(e, Contract), ("Wrong type %s (%r)"
                                                 % (type(e), e))
        return Tuple(length, elements, where=where)


# if you use contract instead of simple_contract, it will be matched as And


inside = (S('(') - contract_expression - S(')')) | or_contract
inside.setName('Any contract for tuple elements (use parenthesis for AND)')

elements = (Group(S('(') - inside - ZeroOrMore(S(',')
                                            - inside) - S(')'))('elements'))
elements.setName('Tuple elements contract.')


length = Group(S('[') - contract_expression - S(']'))('length')
length.setName('Tuple length contract.')

tuple_contract = Keyword('tuple') - O(length | elements)
tuple_contract.setName('tuple contract')

add_contract(tuple_contract.setParseAction(Tuple.parse_action))
add_keyword('tuple')

