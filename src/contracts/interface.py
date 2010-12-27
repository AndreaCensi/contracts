from copy import deepcopy
from .syntax import lineno, col

class Where(object):
    ''' An object of this class represents a place in a file. 
    
    All parsed elements contain a reference to a :py:class:`Where` object
    so that we can output pretty error messages.
    '''
    def __init__(self, string,
                 character=None, line=None, column=None):
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
    ''' The base class for the exceptions thrown by this module. '''
    pass

class ContractSyntaxError(ContractException):
    ''' Exception thrown when there is a syntax error in the contracts. '''
    
    def __init__(self, error, where=None):
        self.error = error
        self.where = where
        
    def __str__(self):
        s = self.error
        s += "\n\n" + add_prefix(self.where.__str__(), ' ')
        return s 

    
class ContractNotRespected(ContractException):
    ''' Exception thrown when a value does not respect a contract. '''
    
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
            # TODO: add config for more verbose messages?
            # msg += '\n                    %r ' % contract
        return msg



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
        


class Context(object):
    ''' Class that represents the context for checking an expression. 
    
        For now it is mostly a glorified dictionary, but perhaps in the
        future it will be something more.
    '''
    class BoundVariable(object):
        def __init__(self, value, description, origin):
            self.value = value
            self.description = description
            self.origin = origin
            
        def __repr__(self):
            return "{0!r}".format(self.value)

    def __init__(self):
        self._variables = {}
        
    def has_variable(self, name):
        return name in self._variables
    
    def get_variable(self, name):
        assert self.has_variable(name)
        return self._variables[name].value
    
    def set_variable(self, name, value, description=None, origin=None):
        assert not self.has_variable(name)
        self._variables[name] = Context.BoundVariable(value, description, origin)
    
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
        assert where is None or isinstance(where, Where), 'Wrong type %s' % where
        self.where = where
    
    def check(self, value):
        ''' Checks that the value satisfies this contract. 
        
            :raise: ContractNotRespected
        '''
        context = Context()
        return self.check_contract(context, value)
    
    def fail(self, value):
        ''' Checks that the value **does not** respect this contract.
            Raises an exception if it does. 
           
           :raise: ValueError 
        '''    
        try:
            context = self.check(value)
        except ContractNotRespected:
            pass
        else:
            msg = 'I did not expect that this value would satisfy this contract.\n'
            msg += '-    value: %s\n' % describe_value(value)
            msg += '- contract: %s\n' % self
            msg += '-  context: %r' % context
            raise ValueError(msg)
        
    def check_contract(self, context, value): #@UnusedVariable
        ''' 
            Checks that value is ok with this contract in the specific 
            context. This is the function that subclasses must implement.
            
            :param context: The context in which expressions are evaluated.
            :type context: ``class(Contract)``
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
            
            It must hold that: ``eval(contract.__repr__()) == contract``.
            This is checked in the unit-tests.

            Example:
            
            >>> from contracts import parse
            >>> contract = parse('list[N]')
            >>> contract.__repr__()
            "List(BindVariable('N',int),None)"
            
            All the symbols you need to eval() the expression are in 
            :py:mod:`contracts.library`.
            
            >>> from contracts.library import *
            >>> contract == eval("%r"%contract)
            True

        '''
        assert False, 'Not implemented in %r' % self.__class__  # pragma: no cover

    def __str__(self):
        ''' Returns a string representation of a contract that can be 
            reparsed by :py:func:`contracts.parse()`.
            
            It must hold that: ``parse(str(contract)) == contract``.
            This is checked in the unit-tests.
            
            Example:
            
            >>> from contracts import parse
            >>> spec = 'list[N]' 
            >>> contract = parse(spec)
            >>> contract
            List(BindVariable('N',int),None)
            >>> str(contract) == spec
            True
            
            The expressions generated by :py:func:`Contract.__str__` will be
            exactly the same as what was parsed (this is checked in the 
            unittests as well) if and only if the expression is "minimal". 
            If it isn't (there is whitespace or redundant symbols), 
            the returned expression will be an equivalent minimal one.
            
            Example with extra parenthesis and whitespace:
            
            >>> from contracts import parse
            >>> verbose_spec = 'list[((N))]( int, > 0)' 
            >>> contract = parse(verbose_spec)
            >>> str(contract)
            'list[N](int,>0)'
            
            Example that removes extra parentheses around arithmetic operators:
            
            >>> verbose_spec = '=1+(1*2)+(2+4)' 
            >>> str(parse(verbose_spec))
            '=1+1*2+2+4'
            
            This is an example with logical operators precedence. The AND
            operator ``,`` (comma) has more precedence than the OR (``|``).
            
            >>> verbose_spec = '(a|(b,c)),e' 
            >>> str(parse(verbose_spec))
            '(a|b,c),e'
            
            Not that only the outer parenthesis is kept as it is the only one 
            needed.
            
            
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
        s = "{0!r}".format(x)
        
        if len(s) > clip:
            s = "%s... [clip]" % s[:clip]

        # python 2
        from types import ClassType
        if isinstance(x, ClassType):
            class_name = '(old-style class type) %s' % x
        else:
            class_name = ' %s' % x.__class__.__name__

        return 'Instance of %s: %s' % (class_name, s)
        
         
    
