from ..interface import Contract, ContractNotRespected, RValue
from ..syntax import (W, oneOf, FollowedBy, NotAny, Keyword, MatchFirst, Literal, Or,
                      White)                


class BindVariable(Contract):
    
    def __init__(self, variable, allowed_types, where=None):
        assert isinstance(variable, str) and len(variable) == 1
        assert allowed_types, '%r' % allowed_types
        Contract.__init__(self, where)
        self.variable = variable
        self.allowed_types = allowed_types
    
    def check_contract(self, context, value):
        if context.has_variable(self.variable):
            expected = context.get_variable(self.variable)
            if not (expected == value):
                # TODO: add where it was bound
                error = ('Expected that %r = %r, got %r.' % 
                         (self.variable, expected, value))
                raise ContractNotRespected(contract=self, error=error,
                                           value=value, context=context)
            
        else:
            # bound variable
            if not isinstance(value, self.allowed_types):
                error = ('Variable %r can only bind to %r, not %r.' % 
                         (self.variable, self.allowed_types,
                          value.__class__.__name__))
                raise ContractNotRespected(self, error, value, context)
            
            context.set_variable(self.variable, value, origin=self)
            
    def __str__(self):
        return self.variable
        
    def __repr__(self):
        # XXX: invalid if tuple
        return 'BindVariable(%r,%s)' % (self.variable, self.allowed_types.__name__)
        
    @staticmethod
    def parse_action(allowed_types):
        def parse(s, loc, tokens):
            where = W(s, loc)
            variable = tokens[0]
            assert len(variable) == 1, \
                    'Wrong syntax, matched %r as variable in %r.' % (variable, s)
            # print ('Matched %r as variable in %r.' % (variable, s))
            return BindVariable(variable, allowed_types, where=where)
        return parse


class VariableRef(RValue):
    def __init__(self, variable, where=None):
        assert isinstance(variable, str)
        self.where = where
        self.variable = variable
        
    def eval(self, context): # XXX
        var = self.variable
        if not context.has_variable(var):
            raise ValueError('Unknown variable %r.' % var)
        return context.get_variable(var)

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
int_variables = oneOf(alphabetu.split()) + FollowedBy(NotAny(oneOf(nofollow.split())))
misc_variables = oneOf(alphabetl.split()) + FollowedBy(NotAny(oneOf(alphabetl.split())))
int_variables_ref = int_variables.copy().setParseAction(VariableRef.parse_action)
misc_variables_ref = misc_variables.copy().setParseAction(VariableRef.parse_action) 

#int_variables = oneOf(alphabetu.split()) + FollowedBy(White() ^ 'x')
 
# These must be followed by whitespace; punctuation
#misc_variables = oneOf(alphabet.lower()) + FollowedBy(White()) 

nofollow = 'a b c d e f g h i j k l m n o p q r s t u w v   y z'
nofollow += ' * - + /'
int_variables2 = oneOf(alphabetu.split()) + FollowedBy(NotAny(oneOf(nofollow.split())))
misc_variables2 = oneOf(alphabetl.split()) + FollowedBy(NotAny(oneOf(alphabetl.split())))
int_variables_contract = int_variables2.setParseAction(BindVariable.parse_action(int))
misc_variables_contract = misc_variables2.setParseAction(BindVariable.parse_action(object))  


