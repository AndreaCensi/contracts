from copy import deepcopy
from types import NoneType

# XXX: remove
from procgraph.core.exceptions import add_prefix

class ContractException(Exception):
    pass

class ContractSyntaxError(ContractException):
    ''' A syntactic error by who wrote the model spec.'''
    def __init__(self, error, where=None):
        self.error = error
        self.where = where
        
    def __str__(self):
        s = self.error
        s += "\n\n" + add_prefix(self.where.__str__(), ' ')
        return s 

    
class ContractNotRespected(ContractException):
    def __init__(self, contract, error, value, context):
        self.contract = contract
        self.error = error
        self.value = value
        self.context = context
        self.stack = []
        
    def __str__(self):
        msg = 'Contract breach: ' + str(self.error) + '\n'
        msg += '-    value:  %s \n' % describe_value(self.value)
        W = 80
        cs = "%s" % self.contract
        cons = "%s" % self.context
        if cons:
            cons = '(context: %s)' % cons
        cons = cons.rjust(W - len(cs))
        msg += '- contract:  %s  %s\n' % (cs, cons)
        
        for (contract, context, value) in self.stack:
            if contract == self.contract: continue
            
            contexts = "%s" % context
            if contexts:
                contexts = ('(context: %s)' % contexts)
            msg += ('\n (checking %s %s for value  %s' % 
                           (contract, contexts, describe_value(value)))
        return msg
    
class ContractSemanticError(ContractException):
    
    def __init__(self, contract, error, context):
        self.contract = contract
        self.error = error
        self.context = context
        
    def __str__(self):
        msg = 'Contract semantic error: ' + str(self.error) + '\n'
        msg += '- context: %r\n' % self.context
        msg += '- contract: %r\n' % self.contract
        return msg
        
class BoundVariable:
    def __init__(self, value, description, origin):
        self.value = value
        self.description = description
        self.origin = origin
        
    def __repr__(self):
        return "%r" % self.value


class RValue:
    def eval(self, context):
        pass 

    def __eq__(self, other):
        members = self.__dict__.keys()
        members.remove('where')
        for m in members:
            mine = getattr(self, m)
            his = getattr(other, m)
            if not(mine == his): # NOTE: different than (mine != his)
                print('In %s: Failed on member %r:\n- %r (%s) vs\n- %r (%s)' % 
                      (self.__class__.__name__,
                       m, mine, mine.__class__.__name__,
                       his, his.__class__.__name__))
                return False
        return True

class SimpleRValue(RValue):
    def __init__(self, value, where=None):
        self.value = value
        self.where = where
        
    def __str__(self):
        return "%s" % self.value
    
    def __repr__(self):
        return "SimpleRValue(%r)" % self.value
    
    def eval(self, context): #@UnusedVariable
        return self.value
                   
    
class VariableRef(RValue):
    def __init__(self, variable, where=None):
        assert isinstance(variable, str)
        self.where = where
        self.variable = variable
        
    def eval(self, context):
        var = self.variable
        if not context.has_variable(var):
            msg = 'Unknown variable %r.' % var
            raise ContractSemanticError(None, msg, context)
        return context.get_variable(var)

    def __repr__(self):
        return "VariableRef(%r)" % self.variable
    
    def __str__(self):
        return "%s" % self.variable

class Context:
    ''' Class that represents the context for checking an expression. '''
        
    def __init__(self):
        self._variables = {}
        
    def has_variable(self, name):
        return name in self._variables
    
    def get_variable(self, name):
        assert self.has_variable(name)
        return self._variables[name].value
    
    def set_variable(self, name, value, description=None, origin=None):
        assert not self.has_variable(name)
        # print 'Set %s = %r' % (name, value)
        self._variables[name] = BoundVariable(value, description, origin)
    
    def eval(self, value, contract_ref=None): # XXX:
        assert isinstance(value, RValue)    
        return value.eval(self)
    
    def copy(self):
        ''' Returns a copy of this context. '''
        return deepcopy(self)
    
    def __repr__(self):
        return 'Context(%r)' % self._variables
    
    def __str__(self):
        return ", ".join("%s=%s" % (k, v) for (k, v) in self._variables.items())
        
class Contract:
    
    def __init__(self, where):
        # XXX
        from procgraph.core.parsing_elements import Where
        assert isinstance(where, (NoneType, Where)), 'Wrong type %s' % where
        self.where = where
    
    def check_contract(self, context, value):
        ''' 
            Checks that value is ok with this contract in the specific 
            context. 
        '''
        raise ValueError('You did not implement check_contract() for %s.' % 
                         self.__class__.__name__)
    
    def _check_contract(self, context, value):
        ''' Recursively checks the contracts; it calls check_contract,
            but the error is wrapped recursively. '''
        contextc = context.copy()
        try: 
            self.check_contract(context, value)
        except ContractNotRespected as e:
            e.stack.append((self, contextc, value))
            raise
    
    
    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        members = self.__dict__.keys()
        members.remove('where')
        
        hismembers = other.__dict__.keys()
        hismembers.remove('where')
        if len(members) != len(hismembers):
            return False
        
        for m in members:
            mine = getattr(self, m)
            if not hasattr(other, m):
                return False
            his = getattr(other, m)
            if not(mine == his): # NOTE: different than (mine != his)
#                print('In %s: Failed on member %r:\n- %r (%s) vs\n- %r (%s)' % 
#                      (self.__class__.__name__,
#                       m, mine, mine.__class__.__name__,
#                       his, his.__class__.__name__))
                return False
        return True
        
def describe_value(x):
    ''' Describes an object, for use in the error messages. '''
    if hasattr(x, 'shape') and hasattr(x, 'dtype'):
        return 'ndarray with shape %s, dtype %s' % (x.shape, x.dtype)
    else:
        if isinstance(x, tuple):
            s = x.__repr__() # XXX: use format()
        else:
            s = "%r" % x
        if len(s) > 20:
            s = "%s... [clip]" % s[:20]
#        else:
#            s = '%r' % s
        return 'Instance of %s: %s' % (x.__class__.__name__, s)
        
        
         
    
    
    
    
