from copy import deepcopy
from types import NoneType
from pyparsing import lineno, col

class Where:
    ''' An object of this class represents a place in a file. 
    
    All parsed elements contain a reference to a :py:class:`Where` object
    so that we can output pretty error messages.
    '''
    def __init__(self, filename, string,
                 character=None, line=None, column=None):
        self.filename = filename
        self.string = string
        if character is None:
            assert line is not None and column is not None
            self.line = line
            self.col = column
            self.character = None
        else:
            assert line is None and column is None
            self.character = character
            self.line = lineno(character, string)
            self.col = col(character, string)

    def __str__(self):
        s = ''
        s += 'In file %s:\n' % self.filename
        context = 3;
        lines = self.string.split('\n')
        start = max(0, self.line - context)
        pattern = 'line %2d >'
        for i in range(start, self.line):
            s += ("%s%s\n" % (pattern % (i + 1), lines[i]))
            
        fill = len(pattern % (i + 1))
        space = ' ' * fill + ' ' * (self.col - 1) 
        s += space + '^\n'
        s += space + '|\n'
        s += space + 'here or nearby'
        return s
    
def add_prefix(s, prefix):
    result = ""
    for l in s.split('\n'):
        result += prefix + l + '\n'
    # chop last newline
    result = result[:-1]
    return result

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
        assert isinstance(contract, Contract)
        assert isinstance(context, Context)
        assert isinstance(error, str)
        
        self.contract = contract
        self.error = error
        self.value = value
        self.context = context
        self.stack = []
        
    def __str__(self):
        msg = str(self.error)# + '\n'
#        msg += '-    value:  %s \n' % describe_value(self.value)
#        W = 80
#        cs = "%s" % self.contract
#        cons = "%s" % self.context
#        if cons:
#            cons = '(context: %s)' % cons
#        cons = cons.rjust(W - len(cs))
#        msg += '- contract:  %s  %s' % (cs, cons)
#        
        for (contract, context, value) in self.stack:
        #    if contract == self.contract: continue
            
            contexts = "%s" % context
            if contexts:
                contexts = ('(context: %s)' % contexts)
                
            cons = ("%s %s" % (contract, contexts)).ljust(30)
            msg += ('\n context: checking: %s  for value: %s' % 
                           (cons, describe_value(value)))
        return msg

class BoundVariable:
    def __init__(self, value, description, origin):
        self.value = value
        self.description = description
        self.origin = origin
        
    def __repr__(self):
        return "{0!r}".format(self.value)


class RValue:
    def eval(self, context):
        ''' Can raise ValueError; will be wrapped in ContractNotRespected. '''
        raise ValueError('Not implemented in %r' % self.__class__) 

    def __eq__(self, other):
        members = self.__dict__.keys()
        members.remove('where')
        for m in members:
            mine = getattr(self, m)
            his = getattr(other, m)
            if not(mine == his): # NOTE: different than (mine != his)
#                print('In %s: Failed on member %r:\n- %r (%s) vs\n- %r (%s)' % 
#                      (self.__class__.__name__,
#                       m, mine, mine.__class__.__name__,
#                       his, his.__class__.__name__))
                return False
        return True

class SimpleRValue(RValue):
    def __init__(self, value, where=None):
        self.value = value
        self.where = where
        
    def __str__(self):
        return "{0!s}".format(self.value)
    
    def __repr__(self):
        return "SimpleRValue({0!r})".format(self.value)
    
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
            raise ValueError('Unknown variable %r.' % var)
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
    
    def eval(self, value, contract): # XXX:
        assert isinstance(value, RValue)
        try:    
            return value.eval(self)
        except ValueError as e:
            return ContractNotRespected(contract, "%s" % e, value, self)
    
    def copy(self):
        ''' Returns a copy of this context. '''
        return deepcopy(self)
    
    # dict interface
    def __contains__(self, key):
        return self.has_variable(key)
    def __getitem__(self, key):
        return self.get_variable(key)
                       
    def __repr__(self):
        return 'Context(%r)' % self._variables
    
    def __str__(self):
        return ", ".join("%s=%s" % (k, v) for (k, v) in self._variables.items())
        
class Contract:
    
    def __init__(self, where):
        assert isinstance(where, (NoneType, Where)), 'Wrong type %s' % where
        self.where = where
    
    def check(self, value):
        ''' Public function -- initializes an empty context. '''
        context = Context()
        return self.check_contract(context, value)
        
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
            
        clip = 50
        if len(s) > clip:
            s = "%s... [clip]" % s[:clip]

        return 'Instance of %s: %s' % (x.__class__.__name__, s)
        
         
    
