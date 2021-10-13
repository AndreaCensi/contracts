#cython: language_level=3, annotation_typing=True, c_string_encoding=utf-8, boundscheck=False, wraparound=True, initializedcheck=False
# -*- coding: utf-8 -*-
import sys
from abc import ABCMeta, abstractmethod
from .metaclass import with_metaclass


class Where(object):
    """
        An object of this class represents a place in a file, or an interval.

        All parsed elements contain a reference to a :py:class:`Where` object
        so that we can output pretty error messages.
        
        
        Character should be >= len(string) (possibly outside the string).
        Character_end should be >= character (so that you can splice with 
        string[character:character_end])
    """

    def __init__(self, string, character, character_end=None):
        from Aspidites._vendor.contracts.utils import raise_desc
        if not isinstance(string, basestring):
            msg = 'I expect the string to be a str, not %r' % string
            raise ValueError(msg)

        if not (0 <= character <= len(string)):
            msg = ('Invalid character loc %s for string of len %s.' %
                   (character, len(string)))
            raise_desc(ValueError, msg, string=string.__repr__())
            # Advance pointer if whitespace
            # if False:
            #     while string[character] == ' ':
            #         if character_end is not None:
            #             assert character <= character_end
            #         if (character < (len(string) - 2)) and ((character_end is None)
            #                                             or (character <= character_end - 1)):
            #             character += 1
            #         else:
            #             break  
        self.line, self.col = line_and_col(character, string)

        if character_end is not None:
            if not (0 <= character_end <= len(string)):
                msg = ('Invalid character_end loc %s for string of len %s.' %
                       (character_end, len(string)))

                raise_desc(ValueError, msg, string=string.__repr__())

            if not (character_end >= character):
                msg = 'Invalid interval [%d:%d]' % (character, character_end)
                raise ValueError(msg)

            self.line_end, self.col_end = line_and_col(character_end, string)
        else:
            self.line_end, self.col_end = None, None

        self.string = string
        self.character = character
        self.character_end = character_end
        self.filename = None

    def get_substring(self):
        """ Returns the substring to which we refer. Raises error if character_end is None """
        from Aspidites._vendor.contracts.utils import raise_desc

        if self.character_end is None:
            msg = 'Character end is None'
            raise_desc(ValueError, msg, where=self)
        return self.string[self.character:self.character_end]

    def __repr__(self):
        if self.character_end is not None:
            part = self.string[self.character:self.character_end]
            return 'Where(%r)' % part
        else:
            return 'Where(s=...,char=%s-%s,line=%s,col=%s)' % (self.character, self.character_end, self.line, self.col)

    def with_filename(self, filename):
        # if self.character is not None:
        w2 = Where(string=self.string,
                       character=self.character, character_end=self.character_end)
        # else:
        #     w2 = Where(string=self.string, line=self.line, column=self.col)
        w2.filename = filename
        return w2

    def __str__(self):
        return format_where(self)


# mark = 'here or nearby'
def format_where(w, context_before=3, mark=None, arrow=True,
                 use_unicode=True, no_mark_arrow_if_longer_than=3):
    s = u''
    if w.filename:
        s += 'In file %r:\n' % w.filename
    lines = w.string.split('\n')
    start = max(0, w.line - context_before)
    pattern = 'line %2d |'
    i = 0
    maxi = i + 1
    assert 0 <= w.line < len(lines), (w.character, w.line, w.string.__repr__())

    # skip only initial empty lines - if one was written do not skip
    one_written = False
    for i in range(start, w.line + 1):
        # suppress empty lines
        if one_written or lines[i].strip():
            s += (u"%s%s\n" % (pattern % (i + 1), lines[i]))
            one_written = True

    fill = len(pattern % maxi)

    # select the space before the string in the same column
    char0 = location(w.line, 0, w.string)  # from col 0
    char0_end = location(w.line, w.col, w.string)  # to w.col
    space_before = Where(w.string, char0, char0_end)

    nindent = printable_length_where(space_before)
    space = u' ' * fill + u' ' * nindent
    if w.col_end is not None:
        if w.line == w.line_end:
            num_highlight = printable_length_where(w)
            s += space + u'~' * num_highlight + '\n'
            space += u' ' * (num_highlight / 2)
        else:
            # cannot highlight if on different lines
            num_highlight = None
            pass
    else:
        num_highlight = None
    # Do not add the arrow and the mark if we have a long underline string 

    disable_mark_arrow = (num_highlight is not None) and (no_mark_arrow_if_longer_than < num_highlight)

    if not disable_mark_arrow:
        if arrow:
            if use_unicode:
                s += space + u'↑\n'
            else:
                s += space + u'^\n'
                s += space + u'|\n'

        if mark is not None:
            s += space + mark

    s = s.rstrip()

    #     from .utils import indent
    #     s +='\n' + indent(w.string, '> ')
    return s


def printable_length_where(w):
    """ Returns the printable length of the substring """
    sub = w.string[w.character:w.character_end]
    # return len(stype(sub, 'utf-8'))
    # I am not really sure this is what we want
    return len(str(sub))


from Aspidites._vendor._compat import basestring


def line_and_col(loc, strg):
    """Returns (line, col), both 0 based."""
    from .utils import check_isinstance
    check_isinstance(loc, int)
    check_isinstance(strg, basestring)
    # first find the line 
    lines = strg.split('\n')

    if loc == len(strg):
        # Special case: we mark the end of the string
        last_line = len(lines) - 1
        last_char = len(lines[-1])
        return last_line, last_char

    if loc > len(strg):
        msg = ('Invalid loc = %d for s of len %d (%r)' %
               (loc, len(strg), strg))
        raise ValueError(msg)

    res_line = 0
    l = loc
    while True:
        if not lines:
            assert loc == 0, (loc, strg.__repr__())
            break

        first = lines[0]
        if l >= len(first) + len('\n'):
            lines = lines[1:]
            l -= (len(first) + len('\n'))
            res_line += 1
        else:
            break
    res_col = l
    inverse = location(res_line, res_col, strg)
    if inverse != loc:
        msg = 'Could not find line and col'
        from .utils import raise_desc
        raise_desc(AssertionError, msg, s=strg, loc=loc, res_line=res_line,
                   res_col=res_col, loc_recon=inverse)

    return (res_line, res_col)


def location(line, col, s):
    from .utils import check_isinstance
    check_isinstance(line, int)
    check_isinstance(col, int)
    check_isinstance(s, basestring)

    lines = s.split('\n')
    previous_lines = sum(len(l) + len('\n') for l in lines[:line])
    offset = col
    return previous_lines + offset


def add_prefix(s, prefix):
    from Aspidites._vendor.contracts import check_isinstance
    check_isinstance(s, basestring)
    check_isinstance(prefix, basestring)
    result = ""
    for l in s.split('\n'):
        result += prefix + l + '\n'
    # chop last newline
    result = result[:-1]
    return result


class ContractException(Exception):
    """ The base class for the exceptions thrown by this module. """


class MissingContract(ContractException):
    pass


class ContractDefinitionError(ContractException):
    """ Thrown when defining the contracts """

    def copy(self):
        """ Returns a copy of the exception so we can re-raise it by erasing the stack. """
        # print('type is %r, args = %s' % (type(self), self.args))
        return type(self)(*self.args)


class ExternalScopedVariableNotFound(ContractDefinitionError):

    def __init__(self, token):
        ContractDefinitionError.__init__(self, token)

    def __str__(self):
        token = self.get_token()
        return 'Token not found: %r.' % (token)

    def get_token(self):
        return self.args[0]


class CannotDecorateClassmethods(ContractDefinitionError):
    pass


class ContractSyntaxError(ContractDefinitionError):
    """ Exception thrown when there is a syntax error in the contracts. """

    def __init__(self, error, where=None):
        self.error = error
        self.where = where
        ContractDefinitionError.__init__(self, error, where)
        self.message = self.__str__()

    def __str__(self):
        error, where = self.args
        s = error
        if where is not None:
            s += "\n\n" + add_prefix(where.__str__(), ' ')
        return s


class ContractNotRespected(ContractException):
    """ Exception thrown when a value does not respect a contract. """

    def __init__(self, contract, error, value, context):
        # XXX: solves pickling problem in multiprocess problem, but not the
        # real solution
        Exception.__init__(self, contract, error, value, context)
        assert isinstance(contract, Contract), contract
        assert isinstance(context, dict), context
        assert isinstance(error, basestring), error

        self.contract = contract
        self.error = error
        self.value = value
        self.context = context
        self.stack = []

    def __str__(self):
        msg = str(self.error)

        def context_to_string(context):
            keys = sorted(context)

            # don't display these two if are not used
            for x in ['args', 'kwargs']:
                if x in keys and not context[x]:
                    keys.remove(x)

            try:
                varss = ['- %s: %s' % (k, describe_value(context[k], clip=70))
                         for k in keys]
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

        if tuple(context0.keys()) == ("",):  # test for an empty or empty-like dict
            msg += ('\nVariables bound in inner context:\n%s'
                    % context_to_string(context0))

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


class RValue(with_metaclass(ABCMeta, object)):

    @abstractmethod
    def eval(self, context):  # @UnusedVariable @ReservedAssignment
        """ Can raise ValueError; will be wrapped in ContractNotRespected. """

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.__repr__() == other.__repr__())

    def __hash__(self):
        return hash(self.__repr__())

    @abstractmethod
    def __repr__(self):
        """ Same constraints as :py:func:`Contract.__repr__()`. """

    @abstractmethod
    def __str__(self):
        """ Same constraints as :py:func:`Contract.__str__()`. """


def eval_in_context(context, value, contract):
    assert isinstance(contract, Contract)
    assert isinstance(value, RValue), describe_value(value)
    try:
        return value.eval(context)
    except ValueError as e:
        msg = 'Error while evaluating RValue %r: %s' % (value, e)
        raise ContractNotRespected(contract, msg, value, context)


class Contract(with_metaclass(ABCMeta, object)):

    __slots__ = ('__contract__', 'where')

    def __init__(self, where):
        assert ((where is None) or
                (isinstance(where, Where), 'Wrong type %s' % where))
        self.where = where
        self.__contract__ = True
        self.enable()

    def enable(self):
        self._enabled = True

    def disable(self):
        self._enabled = False

    def enabled(self):
        return self._enabled

    def check(self, value):
        """
            Checks that the value satisfies this contract.

            :raise: ContractNotRespected
        """
        return self.check_contract({}, value, silent=False)

    def fail(self, value):
        """
            Checks that the value **does not** respect this contract.
            Raises an exception if it does.

            :raise: ValueError
        """
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
    def check_contract(self, context, value, silent):  # @UnusedVariable
        """
            Checks that value is ok with this contract in the specific
            context. This is the function that subclasses must implement.

            If silent = False, do not bother with creating detailed error messages yet.
            This is for performance optimization. 
            
            :param context: The context in which expressions are evaluated.
            :type context:
        """

    def _check_contract(self, context, value, silent):
        """ Recursively checks the contracts; it calls check_contract,
            but the error is wrapped recursively. This is the function
            that subclasses must call when checking their sub-contracts.
        """
        if not self._enabled:
            return

        variables = context.copy()
        try:
            self.check_contract(context, value, silent)
        except ContractNotRespected as e:
            e.stack.append((self, variables, value))
            raise

    @abstractmethod
    def __repr__(self):
        """
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

        """

    @abstractmethod
    def __str__(self):
        """ Returns a string representation of a contract that can be
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


        """

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.__repr__() == other.__repr__())


inPy2 = sys.version_info[0] == 2
if inPy2:  # pragma: no cover
    from types import ClassType


def clipped_repr(x, clip):
    s = "{0!r}".format(x)
    if len(s) > clip:
        clip_tag = '... [clip]'
        cut = clip - len(clip_tag)
        s = "%s%s" % (s[:cut], clip_tag)
    return s


def remove_newlines(s):
    return s.replace('\n', ' ')


def describe_type(x):
    """ Returns a friendly description of the type of x. """
    if inPy2 and isinstance(x, ClassType):  # pragma: no cover
        class_name = '(old-style class) %s' % x
    else:
        if hasattr(x, '__class__'):
            c = x.__class__
            if hasattr(x, '__name__'):
                class_name = '%s' % c.__name__
            else:
                class_name = str(c)
        else:
            # for extension classes (spmatrix)
            class_name = str(type(x))

    return class_name


def describe_value(x, clip=80):
    """ Describes an object, for use in the error messages.
        Short description, no multiline.
    """
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


def describe_value_multiline(x):  # pragma: no cover
    """ Describes an object, for use in the error messages. """
    if hasattr(x, 'shape') and hasattr(x, 'dtype'):
        # XXX this fails for bs4, Tag
        if x.shape is not None:
            shape_desc = 'x'.join(str(i) for i in x.shape)
            desc = 'array[%r](%s) ' % (shape_desc, x.dtype)
            final = desc + '\n' + x.__repr__()
            return final
        else:
            return x.__repr__()
    else:
        if isinstance(x, basestring):
            if x == '': return "''"
            return x
        # XXX: this does not represent strings

        #             if '\n' in x:
        #                 # long multiline
        #                 return x
        #             else:
        #                 # short string
        #                 return x.__repr__()
        else:
            class_name = describe_type(x)
            # TODO: add all types to describe_value_multiline
            desc = 'Instance of %s.' % class_name
            try:
                # This fails for classes
                final = "{}\n{}".format(desc, x.__repr__())
            except: # XXX
                final = "%s\n%s" % (desc, x)

            return final
