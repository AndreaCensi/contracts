from ..interface import Contract, ContractNotRespected, describe_value
from ..syntax import (Combine, Word, W, alphas, alphanums, oneOf,
                      ParseException)


class Extension(Contract):

    registrar = {}

    def __init__(self, identifier, where=None):
        assert identifier in Extension.registrar
        self.contract = Extension.registrar[identifier]
        self.identifier = identifier
        Contract.__init__(self, where)

    def __str__(self):
        return self.identifier
#         return Extension.registrar[self.identifier].__str__()

    def __repr__(self):
        return "Extension(%r)" % self.identifier
        # return "new_contract(%r,%s)" % (self.identifier, Extension.registrar[self.identifier])

    def check_contract(self, context, value):
        self.contract._check_contract(context, value)

    @staticmethod
    def parse_action(s, loc, tokens):
        identifier = tokens[0]

        if not identifier in Extension.registrar:
            raise ParseException('Not matching %r' % identifier)

        where = W(s, loc)
        return Extension(identifier, where)

    # We want to be pickable so we do not save self.contract
    # which might point to a lambda
    def __getstate__(self):
        return {'identifier': self.identifier}

    def __setstate__(self, d):
        self.identifier = d['identifier']
        self.contract = Extension.registrar[self.identifier]


class CheckCallable(Contract):

    def __init__(self, callable):  # @ReservedAssignment
        self.callable = callable
        Contract.__init__(self, where=None)

    def check_contract(self, context, value):
        allowed = (ValueError, AssertionError)
        try:
            result = self.callable(value)
        except allowed as e:  # failed
            raise ContractNotRespected(self, str(e), value, context)

        if result in [None, True]:
            # passed
            pass
        elif result == False:
            msg = ('Value does not pass criteria of %s() (module: %s).' % 
                   (self.callable.__name__, self.callable.__module__))
            raise ContractNotRespected(self, msg, value, context)
        else:
            msg = ('I expect that %r returns either True, False, None; or '
                   'raises a ValueError exception. Instead, I got %s.' % 
                   (self.callable, describe_value(value)))
            raise ValueError(msg)

    def __repr__(self):
        ''' Note: this contract is not representable, but anyway it is 
            only used by Extension, which serializes using the identifier. '''
        return 'CheckCallable(%r)' % self.callable

    def __str__(self):
        ''' Note: this contract is not representable, but anyway it is only 
            used by Extension, which serializes using the identifier. '''
        return 'function %s()' % self.callable.__name__


class CheckCallableWithSelf(Contract):
    def __init__(self, callable):  # @ReservedAssignment
        self.callable = callable
        Contract.__init__(self, where=None)

    def check_contract(self, context, value):
        if not 'self' in context:
            msg = ('You can only call this contract in the context of '
                   ' a function call to a regular method.')
            raise ContractNotRespected(self, msg, value, context)

        args = (context['self'], value)
        allowed = (ValueError, AssertionError)
        try:
            result = self.callable(*args)
        except allowed as e:  # failed
            raise ContractNotRespected(self, str(e), value, context)

        if result in [None, True]:
            # passed
            pass
        elif result == False:
            msg = ('Value does not pass criteria of %s() (module: %s).' % 
                   (self.callable.__name__, self.callable.__module__))
            raise ContractNotRespected(self, msg, value, context)
        else:
            msg = ('I expect that %r returns either True, False, None; or '
                   'raises a ValueError exception. Instead, I got %s.' % 
                   (self.callable, describe_value(value)))
            raise ValueError(msg)

    def __repr__(self):
        ''' Note: this contract is not representable, but anyway it is only 
            used by Extension, which serializes using the identifier. '''
        return 'CheckCallableWithSelf(%r)' % self.callable

    def __str__(self):
        ''' Note: this contract is not representable, but anyway it is only 
            used by Extension, which serializes using the identifier. '''
        return 'function %s()' % self.callable.__name__


# lowercase = alphas.lower()
identifier_expression = Combine(oneOf(list(alphas)) + Word('_' + alphanums))

identifier_contract = identifier_expression.copy().setParseAction(
                                                        Extension.parse_action)

