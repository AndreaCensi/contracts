from ..interface import Contract, ContractNotRespected
from ..syntax import (add_contract, W, contract_expression, O, add_keyword,
    Keyword)


class String(Contract):

    def __init__(self, length=None, where=None):
        Contract.__init__(self, where)
        self.length = length
        assert length is None or isinstance(length, Contract)

    def check_contract(self, context, value):
        if not isinstance(value, basestring):
            error = ('Expected an ANSI or unicode string, got %r.'
                     % value.__class__.__name__)
            raise ContractNotRespected(contract=self, error=error,
                                       value=value, context=context)

        if self.length is not None:
            self.length._check_contract(context, len(value))

    def __repr__(self):
        return 'String(%r)' % self.length

    def __str__(self):
        s = 'string'
        if self.length is not None:
            s += '[%s]' % self.length
        return s

    @staticmethod
    def parse_action(s, loc, tokens):
        where = W(s, loc)
        length = tokens.get('length', None)
        return String(length, where=where)


class AnsiString(Contract):

    def __init__(self, length=None, where=None):
        Contract.__init__(self, where)
        self.length = length
        assert length is None or isinstance(length, Contract)

    def check_contract(self, context, value):
        if not isinstance(value, str):
            error = 'Expected an ANSI string, got %r.' % value.__class__.__name__
            raise ContractNotRespected(contract=self, error=error,
                                       value=value, context=context)

        if self.length is not None:
            self.length._check_contract(context, len(value))

    def __repr__(self):
        return 'AnsiString(%r)' % self.length

    def __str__(self):
        s = 'str'
        if self.length is not None:
            s += '[%s]' % self.length
        return s

    @staticmethod
    def parse_action(s, loc, tokens):
        where = W(s, loc)
        length = tokens.get('length', None)
        return AnsiString(length, where=where)


class UnicodeString(Contract):

    def __init__(self, length=None, where=None):
        Contract.__init__(self, where)
        self.length = length
        assert length is None or isinstance(length, Contract)

    def check_contract(self, context, value):
        if not isinstance(value, unicode):
            error = ('Expected a Unicode string, got %r.'
                     % value.__class__.__name__)
            raise ContractNotRespected(contract=self, error=error,
                                       value=value, context=context)

        if self.length is not None:
            self.length._check_contract(context, len(value))

    def __repr__(self):
        return 'UnicodeString(%r)' % self.length

    def __str__(self):
        s = 'unicode'
        if self.length is not None:
            s += '[%s]' % self.length
        return s

    @staticmethod
    def parse_action(s, loc, tokens):
        where = W(s, loc)
        length = tokens.get('length', None)
        return UnicodeString(length, where=where)


string_contract = Keyword('string') + O('[' - contract_expression('length') - ']')
add_keyword('string')

str_contract = Keyword('str') + O('[' - contract_expression('length') - ']')
add_keyword('str')

unicode_contract = Keyword('unicode') + O('[' - contract_expression('length') - ']')
add_keyword('unicode')

add_contract(string_contract.setParseAction(String.parse_action))
add_contract(str_contract.setParseAction(AnsiString.parse_action))
add_contract(unicode_contract.setParseAction(UnicodeString.parse_action))
