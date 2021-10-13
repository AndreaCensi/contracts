#cython: language_level=3, annotation_typing=True, c_string_encoding=utf-8, boundscheck=False, wraparound=False, initializedcheck=False
from ...._vendor._compat import basestring

from ..interface import Contract, ContractNotRespected, RValue, describe_value
from ..syntax import (W, oneOf, FollowedBy, NotAny)


class BindVariable(Contract):

    def __init__(self, variable, allowed_types, where=None):
        assert isinstance(variable, basestring) and len(variable) == 1
        assert allowed_types, '%r' % allowed_types
        Contract.__init__(self, where)
        self.variable = variable
        self.allowed_types = allowed_types

    def check_contract(self, context, value, silent):
        if self.variable in context:
            expected = context[self.variable]
            if not (expected == value):
                error = ('Expected value for %r was: %s\n        instead I received: %s' % (self.variable, describe_value(expected), describe_value(value)))
                raise ContractNotRespected(contract=self, error=error,
                                           value=value, context=context)

        else:
            # bound variable
            if not isinstance(value, self.allowed_types):
                error = ('Variable %r can only bind to %r, not %r.' %
                         (self.variable, self.allowed_types,
                          value.__class__.__name__))
                raise ContractNotRespected(self, error, value, context)

            context[self.variable] = value

    def __str__(self):
        return self.variable

    def __repr__(self):
        # XXX: invalid if tuple
        return 'BindVariable(%r,%s)' % (self.variable,
                                        self.allowed_types.__name__)

    @staticmethod
    def parse_action(allowed_types):
        def parse(s, loc, tokens):
            where = W(s, loc)
            variable = tokens[0]
            assert len(variable) == 1, \
                    ('Wrong syntax, matched %r as variable in %r.'
                     % (variable, s))
            # print ('Matched %r as variable in %r.' % (variable, s))
            return BindVariable(variable, allowed_types, where=where)
        return parse


class VariableRef(RValue):
    def __init__(self, variable, where=None):
        assert isinstance(variable, basestring)
        self.where = where
        self.variable = variable

    def eval(self, context):  # @ReservedAssignment
        var = self.variable
        if not var in context:
            raise ValueError('Unknown variable %r.' % var)
        return context[var]

    def __repr__(self):
        return "VariableRef(%r)" % self.variable

    def __str__(self):
        return "%s" % self.variable

    @staticmethod
    def parse_action(s, loc, tokens):
        where = W(s, loc)
        return VariableRef(tokens[0], where=where)

alphabetu = 'A B C D E F G H I J K L M N O P Q R S T U W V X Y Z '
alphabetl = 'a b c d e f g h i j k l m n o p q r s t u w v x y z '

# Special case: allow an expression like AxBxC
nofollow = 'a b c d e f g h i j k l m n o p q r s t u w v   y z'
# also do not commit if part of word (SEn, a_2)
nofollow += ' A B C D E F G H I J K L M N O P Q R S T U W V X Y Z '
nofollow += ' 0 1 2 3 4 5 6 7 8 9 _'
# but recall 'axis_angle'
int_variables = (oneOf(alphabetu.split())
                  + FollowedBy(NotAny(oneOf(nofollow.split()))))
misc_variables = (oneOf(alphabetl.split())
                  + FollowedBy(NotAny(oneOf(nofollow.split() + ['x']))))
int_variables_ref = int_variables.copy().setParseAction(
                                                    VariableRef.parse_action)
misc_variables_ref = misc_variables.copy().setParseAction(
                                                    VariableRef.parse_action)

#int_variables = oneOf(alphabetu.split()) + FollowedBy(White() ^ 'x')

# These must be followed by whitespace; punctuation
#misc_variables = oneOf(alphabet.lower()) + FollowedBy(White()) 

nofollow = 'a b c d e f g h i j k l m n o p q r s t u w v   y z '
nofollow += ' * - + / '
nofollow += ' A B C D E F G H I J K L M N O P Q R S T U W V X Y Z '
nofollow += ' 0 1 2 3 4 5 6 7 8 9 _'
int_variables2 = (oneOf(alphabetu.split())
                  + FollowedBy(NotAny(oneOf(nofollow.split()))))
misc_variables2 = (oneOf(alphabetl.split())
                   + FollowedBy(NotAny(oneOf(nofollow.split() + ['x']))))
int_variables_contract = int_variables2.setParseAction(
                                                BindVariable.parse_action(int))
misc_variables_contract = misc_variables2.setParseAction(
                                            BindVariable.parse_action(object))


