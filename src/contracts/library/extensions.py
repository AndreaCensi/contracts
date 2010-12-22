from ..interface import Contract, ContractNotRespected, describe_value
from ..syntax import Combine, Word, W, alphas, alphanums, oneOf, add_contract
from pyparsing import ParseFatalException, ParseException

class Extension(Contract):
    
    registrar = {}
    
    def __init__(self, identifier, where=None):
        assert identifier in Extension.registrar
        self.identifier = identifier
        Contract.__init__(self, where)
    
    def __str__(self):
        return self.identifier
    
    def __repr__(self):
        return "Extension(%r)" % self.identifier
    
    def check_contract(self, context, value):
        Extension.registrar[self.identifier]._check_contract(context, value)
        
    @staticmethod
    def parse_action(s, loc, tokens):
        identifier = tokens[0]
        
        where = W(s, loc)
        
        if not identifier in Extension.registrar:
            msg = 'Invalid expression identifier %r.\n' % identifier
            msg += 'I know: %r.\n' % (list(Extension.registrar.keys()))
            msg += str(where)
            # print msg
            raise ParseFatalException(msg)
        
        return Extension(identifier, where)


class CheckCallable(Contract):
    def __init__(self, callable):
        self.callable = callable
        
    def check_contract(self, context, value):
        try:
            result = self.callable(value)
        except ValueError as e: # failed
            raise ContractNotRespected(self, str(e), value, context)
            
        if result in [None, True]: 
            # passed
            pass
        elif result == False:
            msg = 'Value does not pass criteria of %r.' % self.callable
            raise ContractNotRespected(self, msg, value, context)
        else:
            msg = ('I expect that %r returns either True, False, None; or '
                   'raises a ValueError exception. Instead, I got %s.' % 
                   (self.callable, describe_value(value))) 
            raise ValueError(msg)
        
    def __repr__(self):
        ''' Note: this contract is not representable, but anyway it is only used
            by Extension, which serializes using the identifier. '''
        return 'CheckCallable(%r)' % self.callable
 
    def __str__(self):
        ''' Note: this contract is not representable, but anyway it is only used
            by Extension, which serializes using the identifier. '''
        return '@check_callable(%s)' % self.callable
    

#identifier_expression = Combine(oneOf(alphas) + Word('_' + alphanums))
#lowercase = alphas.lower()
identifier_expression = Combine(oneOf(list(alphas)) + Word('_' + alphanums))

identifier_contract = identifier_expression.copy().setParseAction(Extension.parse_action)
#add_contract(identifier_contract)

