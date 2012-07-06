from ..interface import Contract, ContractNotRespected
from ..syntax import (add_contract, W, contract_expression, O, add_keyword,
    Keyword)


# Base class for string contracts
class StringBase(Contract):

    def __init__(self, length=None, where=None):
        Contract.__init__(self, where)
        self.length = length
        assert length is None or isinstance(length, Contract)

    def check_contract(self, context, value):
        if not isinstance(value, self.TYPE):
            error = 'Expected %s, got %r.' % (
                self.DESCRIPTION, value.__class__.__name__)
            raise ContractNotRespected(contract=self, error=error,
                                       value=value, context=context)

        if self.length is not None:
            self.length._check_contract(context, len(value))

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.length)

    def __str__(self):
        s = self.KEYWORD
        if self.length is not None:
            s += '[%s]' % self.length
        return s

    @classmethod
    def parse_action(cls, s, loc, tokens):
        where = W(s, loc)
        length = tokens.get('length', None)
        return cls(length, where=where)


class String(StringBase):
    KEYWORD = 'string'
    TYPE = basestring
    DESCRIPTION = "an ANSI or Unicode string"


class AnsiString(StringBase):
    KEYWORD = 'str'
    TYPE = str
    DESCRIPTION = "an ANSI string"


class UnicodeString(StringBase):
    KEYWORD = 'unicode'
    TYPE = unicode
    DESCRIPTION = "a Unicode string"


for cls in StringBase.__subclasses__():
    contract = (Keyword(cls.KEYWORD) +
                O('[' - contract_expression('length') - ']'))
    add_keyword(cls.KEYWORD)
    add_contract(contract.setParseAction(cls.parse_action))
