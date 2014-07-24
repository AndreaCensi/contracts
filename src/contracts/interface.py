from .syntax import lineno, col
import sys
from abc import abstractmethod, ABCMeta


class Where(object):
    '''
        An object of this class represents a place in a file.

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
        return  s


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

class MissingContract(ContractException):
    pass

class ContractDefinitionError(ContractException):
    """ Thrown when defining the contracts """

class CannotDecorateClassmethods(ContractDefinitionError):
    pass
    
class ContractSyntaxError(ContractDefinitionError):
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
        # XXX: solves pickling problem in multiprocess problem, but not the
        # real solution
        Exception.__init__(self, contract, error, value, context)
        assert isinstance(contract, Contract), contract
        assert isinstance(context, dict), context
        assert isinstance(error, str), error

        self.contract = contract
        self.error = error
        self.value = value
        self.context = context
        self.stack = []

    def __str__(self):
        msg = str(self.error)
        
        def context_to_string(context):
            try:
                varss = ['- %s: %s' % (k, describe_value(v, clip=70))
                         for k, v in context.items()]
                contexts = "\n".join(varss)
            except:
                contexts = '! cannot write context'
            return contexts

        align = []
        for (contract, context, value) in self.stack:  # @UnusedVariable
            # cons = ("%s %s" % (contract, contexts)).ljust(30)
            row = ['checking: %s' % contract,
                    'for value: %s' % describe_value(value, clip=70)]
            align.append(row)
            
        msg += format_table(align, colspacing=3)
        
        context0 = self.stack[0][1]
        if context0:
            msg += ('\nVariables bound in inner context:\n%s' 
                    % context_to_string(self.stack[0][1]))
            
        return msg


def format_table(rows, colspacing=1):
    sizes = []
    for i in range(len(rows[0])):
        sizes.append(max(len(row[i]) for row in rows))
    s = ''
    for row in rows:
        s += '\n'
        for size, cell in zip(sizes, row):
            s += cell.ljust(size)
            s += ' ' * colspacing
    return s


class RValue(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def eval(self, context):  # @UnusedVariable @ReservedAssignment
        ''' Can raise ValueError; will be wrapped in ContractNotRespected. '''

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.__repr__() == other.__repr__())

    @abstractmethod
    def __repr__(self):
        ''' Same constraints as :py:func:`Contract.__repr__()`. '''

    @abstractmethod
    def __str__(self):
        ''' Same constraints as :py:func:`Contract.__str__()`. '''


def eval_in_context(context, value, contract):
    assert isinstance(contract, Contract)
    assert isinstance(value, RValue), describe_value(value)
    try:
        return value.eval(context)
    except ValueError as e:
        msg = 'Error while evaluating RValue %r: %s' % (value, e)
        raise ContractNotRespected(contract, msg, value, context)


class Contract(object):
    __metaclass__ = ABCMeta

    def __init__(self, where):
        assert ((where is None) or
                (isinstance(where, Where), 'Wrong type %s' % where))
        self.where = where
        self.enable()

    def enable(self):
        self._enabled = True

    def disable(self):
        self._enabled = False

    def enabled(self):
        return self._enabled

    def check(self, value):
        '''
            Checks that the value satisfies this contract.

            :raise: ContractNotRespected
        '''
        return self.check_contract({}, value)

    def fail(self, value):
        '''
            Checks that the value **does not** respect this contract.
            Raises an exception if it does.

            :raise: ValueError
        '''
        try:
            context = self.check(value)
        except ContractNotRespected:
            pass
        else:
            msg = ('I did not expect that this value would '
                   'satisfy this contract.\n')
            msg += '-    value: %s\n' % describe_value(value)
            msg += '- contract: %s\n' % self
            msg += '-  context: %r' % context
            raise ValueError(msg)

    @abstractmethod
    def check_contract(self, context, value):  # @UnusedVariable
        ''' 
            Checks that value is ok with this contract in the specific 
            context. This is the function that subclasses must implement.
            
            :param context: The context in which expressions are evaluated.
            :type context: ``class(Contract)``
        '''

    def _check_contract(self, context, value):
        ''' Recursively checks the contracts; it calls check_contract,
            but the error is wrapped recursively. This is the function
            that subclasses must call when checking their sub-contracts. 
        '''
        if not self._enabled:
            return

        variables = context.copy()
        try:
            self.check_contract(context, value)
        except ContractNotRespected as e:
            e.stack.append((self, variables, value))
            raise

    @abstractmethod
    def __repr__(self):
        ''' 
            Returns a string representation of a contract that can be 
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

    @abstractmethod
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

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.__repr__() == other.__repr__())


inPy2 = sys.version_info[0] == 2
if inPy2:
    from types import ClassType


def clipped_repr(x, clip):
    s = "{0!r}".format(x)
    if len(s) > clip:
        clip_tag = '... [clip]'
        cut = clip - len(clip_tag)
        s = "%s%s" % (s[:cut], clip_tag)
    return s

# TODO: add checks for these functions


def remove_newlines(s):
    return s.replace('\n', ' ')


def describe_type(x):
    ''' Returns a friendly description of the type of x. '''
    if inPy2 and isinstance(x, ClassType):
        class_name = '(old-style class) %s' % x
    else:
        if hasattr(x, '__class__'):
            class_name = '%s' % x.__class__.__name__
        else:
            # for extension classes (spmatrix)
            class_name = str(type(x))

    return class_name


def describe_value(x, clip=80):
    ''' Describes an object, for use in the error messages. 
        Short description, no multiline.
    '''
    if hasattr(x, 'shape') and hasattr(x, 'dtype'):
        shape_desc = 'x'.join(str(i) for i in x.shape)
        desc = 'array[%r](%s) ' % (shape_desc, x.dtype)
        final = desc + clipped_repr(x, clip - len(desc))
        return remove_newlines(final)
    else:
        class_name = describe_type(x)
        desc = 'Instance of %s: ' % class_name
        final = desc + clipped_repr(x, clip - len(desc))
        return remove_newlines(final)


def describe_value_multiline(x):
    ''' Describes an object, for use in the error messages. '''
    if hasattr(x, 'shape') and hasattr(x, 'dtype'):
        shape_desc = 'x'.join(str(i) for i in x.shape)
        desc = 'array[%r](%s) ' % (shape_desc, x.dtype)
        final = desc + '\n', x.__repr__()
        return final
    else:
        class_name = describe_type(x)
        # TODO: add all types
        desc = 'Instance of %s.' % class_name
        final = desc +'\n' + x.__repr__()
#         final = desc +'\n' +str(x)
        return final



