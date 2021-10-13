#cython: language_level=3, annotation_typing=True, c_string_encoding=utf-8, boundscheck=False, wraparound=False, initializedcheck=False
from ..interface import Contract, ContractNotRespected, describe_value
from ..syntax import (Combine, Word, W, alphas, alphanums, oneOf,
                      ParseException, ZeroOrMore, S, rvalue,
                      delimitedList, Optional)
from Aspidites._vendor.pyparsing import ParseFatalException


class Extension(Contract):
    registrar = {}

    def __init__(self, identifier, where=None, args=tuple(), kwargs=None):
        assert identifier in Extension.registrar
        self.contract = Extension.registrar[identifier]
        self.identifier = identifier
        self.args = args
        self.kwargs = kwargs or {}
        Contract.__init__(self, where)

    def __str__(self):
        inside = []
        if self.args:
            inside.extend(map(str, self.args))
            
        if self.kwargs:
            ks = sorted(self.kwargs)
            inside.extend(["%s=%s" % (k, self.kwargs[k]) for k in ks])

        s = self.identifier
    
        if inside:
            return self.identifier + "(" + ",".join(inside) + ")"
        else:
            return s

    def __repr__(self):
        if self.args or self.kwargs:
            return ("Extension(%r, args=%r, kwargs=%r)" %
                    (self.identifier, self.args, self.kwargs))

        return "Extension(%r)" % self.identifier

    def check_contract(self, context, value, silent):
        context['args'] = tuple(a.eval(context) for a in self.args)
        context['kwargs'] = dict((k, v.eval(context)) for
                                 k, v in self.kwargs.items())

        # noinspection PyProtectedMember
        self.contract._check_contract(context, value, silent)

    @staticmethod
    def parse_action(s, loc, tokens):
        identifier = tokens[0]
        args = tuple()
        kwargs = {}

        if len(tokens) == 2:
            args, kwargs = tokens[1]
            args = tuple(args)

        if not identifier in Extension.registrar:
            raise ParseException('Unknown extension contract %r' % identifier)
        
        # from contracts.library.separate_context import SeparateContext
        
        contract_ext = Extension.registrar[identifier]
        
        if isinstance(contract_ext, CheckCallable):
            callable_thing = contract_ext.callable 
         
            test_args = ('value',) + args
            # don't move this import
            from Aspidites._vendor.contracts.inspection import check_callable_accepts_these_arguments, InvalidArgs
         
            try:
                check_callable_accepts_these_arguments(callable_thing, test_args, kwargs)
             
            except InvalidArgs as e:
                msg = 'The callable %s cannot accept these arguments ' % callable_thing
                msg += 'args = %s, kwargs = %s ' % (test_args, kwargs)
                msg += '%s' % e
                raise ParseFatalException(msg)

        where = W(s, loc)
        return Extension(identifier, where, args, kwargs)

    # We want to be pickable so we do not save self.contract
    # which might point to a lambda
    def __getstate__(self):
        return {'identifier': self.identifier,
                'args': self.args,
                'kwargs': self.kwargs}

    def __setstate__(self, d):
        self.identifier = d['identifier']
        self.contract = Extension.registrar[self.identifier]
        self.args = d['args']
        self.kwargs = d['kwargs']


class CheckCallable(Contract):

    def __init__(self, callable):
        self.callable = callable
        Contract.__init__(self, where=None)

    def check_contract(self, context, value, silent):
        allowed = (ValueError, AssertionError)
        args = context.get('args', tuple())
        kwargs = context.get('kwargs', {})
        try:
            result = self.callable(value, *args, **kwargs)
        except allowed as e:  # failed
            raise ContractNotRespected(self, str(e), value, context)

        if result in [None, True]:
            # passed
            pass
        elif result == False:
            msg = ('Value does not pass criteria of %s() (module: %s).' %
                   (get_callable_name(self.callable), 
                    get_callable_module(self.callable)))
            raise ContractNotRespected(self, msg, value, context)
        else:
            msg = ('I expect that %r returns either True, False, None; or '
                   'raises a ValueError exception. Instead, I got %s.' %
                   (self.callable, describe_value(value)))
            raise ValueError(msg)

    def __repr__(self):
        """ Note: this contract is not representable, but anyway it is
            only used by Extension, which serializes using the identifier. """
        return 'CheckCallable(%r)' % self.callable

    def __str__(self):
        """ Note: this contract is not representable, but anyway it is only
            used by Extension, which serializes using the identifier. """
        return get_callable_name(callable)


def get_callable_name(c):
    """ Get a displayable name for the callable even if __name__
        is not available. """
    try:
        return c.__name__ + '()'
    except AttributeError:
        return str(c)


def get_callable_module(c):
    try:
        return c.__module__
    except AttributeError:
        return '(No __module__ attr)'


def describe_callable(c):
    return get_callable_name(c) + ' module: %s' % get_callable_module(c)


class CheckCallableWithSelf(Contract):

    def __init__(self, callable):  # @ReservedAssignment
        self.callable = callable
        Contract.__init__(self, where=None)

    def check_contract(self, context, value, silent):
        args = context.get('args', tuple())
        kwargs = context.get('kwargs', {})

        if not 'self' in context:
            msg = ('You can only call this contract in the context of '
                   ' a function call to a regular method.')
            raise ContractNotRespected(self, msg, value, context)

        args = (context['self'], value) + args
        allowed = (ValueError, AssertionError)
        try:
            result = self.callable(*args, **kwargs)
        except allowed as e:  # failed
            raise ContractNotRespected(self, str(e), value, context)

        if result in [None, True]:
            # passed
            pass
        elif result == False:
            msg = ('Value does not pass criteria of %s.' %
                   describe_callable(self.callable))
            raise ContractNotRespected(self, msg, value, context)
        else:
            msg = ('I expect that %r returns either True, False, None; or '
                   'raises a ValueError exception. Instead, I got %s.' %
                   (self.callable, describe_value(value)))
            raise ValueError(msg)

    def __repr__(self):
        """ Note: this contract is not representable, but anyway it is only
            used by Extension, which serializes using the identifier. """
        return 'CheckCallableWithSelf(%r)' % self.callable

    def __str__(self):
        """ Note: this contract is not representable, but anyway it is only
            used by Extension, which serializes using the identifier. """
        return 'function %s()' % get_callable_name(self.callable)


w = Word('_' + alphanums)
arg = rvalue.copy()

kwarg = w + ZeroOrMore(' ') + S('=') + ZeroOrMore(' ') + rvalue
kwarg.setParseAction(lambda s, loc, tokens: {tokens[0]: tokens[1]})


def build_args_kwargs(s, loc, tokens):
    return (tuple(t for t in tokens if not isinstance(t, dict)),
            dict((k, v) for t in tokens if isinstance(t, dict)
                 for k, v in t.items()))


arglist = delimitedList(kwarg | arg)
arglist.setParseAction(build_args_kwargs)

identifier_expression = (Combine(oneOf(list(alphas)) + Word('_' + alphanums)) +
                         Optional(S('(') + arglist + S(')')))


identifier_contract = identifier_expression.copy().setParseAction(
    Extension.parse_action)
