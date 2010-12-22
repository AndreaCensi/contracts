from copy import deepcopy
from types import NoneType
from pyparsing import lineno, col

class Where(object):
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
        if self.filename is not None:
            s += 'In file %s:\n' % self.filename
        context = 3
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
        assert isinstance(contract, Contract), contract
        assert isinstance(context, Context), context
        assert isinstance(error, str), error
        
        self.contract = contract
        self.error = error
        self.value = value
        self.context = context
        self.stack = []
        
    def __str__(self):
        msg = str(self.error) 
        for (contract, context, value) in self.stack:
            contexts = "%s" % context
            if contexts:
                contexts = ('(context: %s)' % contexts)
                
            cons = ("%s %s" % (contract, contexts)).ljust(30)
            msg += ('\n context: checking: %s  for value: %s' % 
                           (cons, describe_value(value)))
            msg += '\n                    %r ' % contract
        return msg

class BoundVariable(object):
    def __init__(self, value, description, origin):
        self.value = value
        self.description = description
        self.origin = origin
        
    def __repr__(self):
        return "{0!r}".format(self.value)


class RValue(object):
    
    def eval(self, context): #@UnusedVariable
        ''' Can raise ValueError; will be wrapped in ContractNotRespected. '''
        assert False, 'Not implemented in %r' % self.__class__  # pragma: no cover 

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and 
                self.__repr__() == other.__repr__())
        
    def __repr__(self):
        ''' Same constraints as :py:func:`Contract.__repr__()`. '''
        assert False, 'Not implemented in %r' % self.__class__  # pragma: no cover

    def __str__(self):
        ''' Same constraints as :py:func:`Contract.__str__()`. '''
        assert False, 'Not implemented in %r' % self.__class__  # pragma: no cover
        

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
        
    def eval(self, context): # XXX
        var = self.variable
        if not context.has_variable(var):
            raise ValueError('Unknown variable %r.' % var)
        return context.get_variable(var)

    def __repr__(self):
        return "VariableRef(%r)" % self.variable
    
    def __str__(self):
        return "%s" % self.variable

class Context(object):
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
        self._variables[name] = BoundVariable(value, description, origin)
    
    def eval(self, value, contract):
        assert isinstance(value, RValue)
        assert isinstance(contract, Contract)
        try:    
            return value.eval(self)
        except ValueError as e:
            msg = 'Error while evaluating RValue %r: %s' % (value, e)
            raise ContractNotRespected(contract, msg, value, self)
    
    def copy(self):
        ''' Returns a copy of this context. '''
        return deepcopy(self)
    
    def __contains__(self, key):
        return self.has_variable(key)
    
    def __getitem__(self, key):
        return self.get_variable(key)
                       
    def __repr__(self):
        return 'Context(%r)' % self._variables
    
    def __str__(self):
        return ", ".join("%s=%s" % (k, v) for (k, v) in list(self._variables.items()))
        
class Contract(object):
    
    def __init__(self, where):
        assert isinstance(where, (NoneType, Where)), 'Wrong type %s' % where
        self.where = where
    
    def check(self, value):
        ''' Checks that the value satisfies this contract. '''
        context = Context()
        return self.check_contract(context, value)
        
    def check_contract(self, context, value): #@UnusedVariable
        ''' 
            Checks that value is ok with this contract in the specific 
            context. This is the function that subclasses must implement.
            
            :param context: The context in which expressions are evaluated.
            :type context: class(Contract)
        '''
        assert False, 'Not implemented in %r' % self.__class__ # pragma: no cover
    
    def _check_contract(self, context, value):
        ''' Recursively checks the contracts; it calls check_contract,
            but the error is wrapped recursively. This is the function
            that subclasses must call when checking their sub-contracts. 
        '''
        assert isinstance(context, Context), context
        contextc = context.copy()
        try: 
            self.check_contract(context, value)
        except ContractNotRespected as e:
            e.stack.append((self, contextc, value))
            raise
    
    def __repr__(self):
        ''' Returns a string representation of a contract that can be 
            evaluated by Python's :py:func:`eval()`.

            It must hold that: ::
            
                eval(contract.__repr__()) == contract
    
            (This is checked in the unit-tests.)

        '''
        assert False, 'Not implemented in %r' % self.__class__  # pragma: no cover

    def __str__(self):
        ''' Returns a string representation of a contract that can be 
            reparsed by :py:func:`contracts.parse()`.
            
            It must hold that: ::
            
                parse(str(contract)) == contract
    
            (This is checked in the unit-tests.)
        '''
        assert False, 'Not implemented in %r' % self.__class__ # pragma: no cover

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and 
                self.__repr__() == other.__repr__())

        
def describe_value(x, clip=50):
    ''' Describes an object, for use in the error messages. '''
    if hasattr(x, 'shape') and hasattr(x, 'dtype'):
        return 'ndarray with shape %s, dtype %s' % (x.shape, x.dtype)
    else:
        if isinstance(x, tuple):
            s = x.__repr__() # XXX: use format()
        else:
            s = "%r" % x
            
        if len(s) > clip:
            s = "%s... [clip]" % s[:clip]

        return 'Instance of %s: %s' % (x.__class__.__name__, s)
        
         
    
