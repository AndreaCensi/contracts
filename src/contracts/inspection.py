# cython: language_level=3, annotation_typing=True, c_string_encoding=utf-8, boundscheck=False, wraparound=True, initializedcheck=False
"""Get useful information from live Python objects.
This is a statically compiled version of the inspect module from the standard library.

This module encapsulates the interface provided by the internal special
attributes (co_*, im_*, tb_*, etc.) in a friendlier fashion.
It also provides some help for examining source code and class layout.

Here are some of the useful functions provided by this module:

    ismodule(), isclass(), ismethod(), isfunction(), isgeneratorfunction(),
        isgenerator(), istraceback(), isframe(), iscode(), isbuiltin(),
        isroutine() - check object types
    getmembers() - get members of an object that satisfy a given condition

    getfile(), getsourcefile(), getsource() - find an object's source code
    getdoc(), getcomments() - get documentation on an object
    getmodule() - determine the module that an object came from
    getclasstree() - arrange classes so as to represent their hierarchy

    getargvalues(), getcallargs() - get info about function arguments
    getfullargspec() - same, with support for Python 3 features
    formatargvalues() - format an argument spec
    getouterframes(), getinnerframes() - get info about frames
    currentframe() - get the current stack frame
    stack(), trace() - get info about frames on the stack or in a traceback

    signature() - get a Signature object for the callable
"""

import ast
import dis
import enum
import importlib.machinery
import linecache
import os
import re
import sys
import types
import warnings
from collections import namedtuple
from typing import Callable
from inspect import FullArgSpec, getfullargspec

inPy2 = sys.version_info[0] == 2

# Create constants for the compiler flags in Include/code.h
# We try to get them from dis to avoid duplication
mod_dict = globals()
for k, v in dis.COMPILER_FLAG_NAMES.items():
    mod_dict["CO_" + v] = k

# See Include/object.h
TPFLAGS_IS_ABSTRACT = 1 << 20


# ----------------------------------------------------------- type-checking
def ismodule(obj):
    """Return true if the object is a module.

    Module objects provide these attributes:
        __cached__      pathname to byte compiled file
        __doc__         documentation string
        __file__        filename (missing for built-in modules)"""
    return isinstance(obj, types.ModuleType)


def isclass(obj):
    """Return true if the object is a class.

    Class objects provide these attributes:
        __doc__         documentation string
        __module__      name of module in which this class was defined"""
    return isinstance(obj, type)


def ismethod(obj):
    """Return true if the object is an instance method.

    Instance method objects provide these attributes:
        __doc__         documentation string
        __name__        name with which this method was defined
        __func__        function object containing implementation of method
        __self__        instance to which this method is bound"""
    return isinstance(obj, types.MethodType)


def isfunction(object):
    """Return true if the object is a user-defined function.

    Function objects provide these attributes:
        __doc__         documentation string
        __name__        name with which this function was defined
        __code__        code object containing compiled function bytecode
        __defaults__    tuple of any default values for arguments
        __globals__     global namespace in which this function was defined
        __annotations__ dict of parameter annotations
        __kwdefaults__  dict of keyword only parameters with defaults"""
    return isinstance(object, types.FunctionType)


def istraceback(object):
    """Return true if the object is a traceback.

    Traceback objects provide these attributes:
        tb_frame        frame object at this level
        tb_lasti        index of last attempted instruction in bytecode
        tb_lineno       current line number in Python source code
        tb_next         next inner traceback object (called by this level)"""
    return isinstance(object, types.TracebackType)


def isframe(object):
    """Return true if the object is a frame object.

    Frame objects provide these attributes:
        f_back          next outer frame object (this frame's caller)
        f_builtins      built-in namespace seen by this frame
        f_code          code object being executed in this frame
        f_globals       global namespace seen by this frame
        f_lasti         index of last attempted instruction in bytecode
        f_lineno        current line number in Python source code
        f_locals        local namespace seen by this frame
        f_trace         tracing function for this frame, or None"""
    return isinstance(object, types.FrameType)


def iscode(object):
    """Return true if the object is a code object.

    Code objects provide these attributes:
        co_argcount         number of arguments (not including *, ** args
                            or keyword only arguments)
        co_code             string of raw compiled bytecode
        co_cellvars         tuple of names of cell variables
        co_consts           tuple of constants used in the bytecode
        co_filename         name of file in which this code object was created
        co_firstlineno      number of first line in Python source code
        co_flags            bitmap: 1=optimized | 2=newlocals | 4=*arg | 8=**arg
                            | 16=nested | 32=generator | 64=nofree | 128=coroutine
                            | 256=iterable_coroutine | 512=async_generator
        co_freevars         tuple of names of free variables
        co_posonlyargcount  number of positional only arguments
        co_kwonlyargcount   number of keyword only arguments (not including ** arg)
        co_lnotab           encoded mapping of line numbers to bytecode indices
        co_name             name with which this code object was defined
        co_names            tuple of names of local variables
        co_nlocals          number of local variables
        co_stacksize        virtual machine stack space required
        co_varnames         tuple of names of arguments and local variables"""
    return isinstance(object, types.CodeType)


def getfile(object):
    """Work out which source or compiled file an object was defined in."""
    if ismodule(object):
        if getattr(object, '__file__', None):
            return object.__file__
        raise TypeError('{!r} is a built-in module'.format(object))
    if isclass(object):
        if hasattr(object, '__module__'):
            module = sys.modules.get(object.__module__)
            if getattr(module, '__file__', None):
                return module.__file__
        raise TypeError('{!r} is a built-in class'.format(object))
    if ismethod(object):
        object = object.__func__
    if isfunction(object):
        object = object.__code__
    if istraceback(object):
        object = object.tb_frame
    if isframe(object):
        object = object.f_code
    if iscode(object):
        return object.co_filename
    raise TypeError('module, class, method, function, traceback, frame, or '
                    'code object was expected, got {}'.format(type(object).__name__))


Arguments = namedtuple('Arguments', 'args, varargs, varkw')


def getabsfile(object, _filename=None):
    """Return an absolute path to the source or compiled file for an object.

    The idea is for each object to have a unique origin, so this routine
    normalizes the result as much as possible."""
    if _filename is None:
        _filename = getsourcefile(object) or getfile(object)
    return os.path.normcase(os.path.abspath(_filename))


modulesbyfile = {}
_filesbymodname = {}


def getmodule(object, _filename=None):
    """Return the module an object was defined in, or None if not found."""
    if ismodule(object):
        return object
    if hasattr(object, '__module__'):
        return sys.modules.get(object.__module__)
    # Try the filename to modulename cache
    if _filename is not None and _filename in modulesbyfile:
        return sys.modules.get(modulesbyfile[_filename])
    # Try the cache again with the absolute file name
    try:
        file = getabsfile(object, _filename)
    except TypeError:
        return None
    if file in modulesbyfile:
        return sys.modules.get(modulesbyfile[file])
    # Update the filename to module name cache and check yet again
    # Copy sys.modules in order to cope with changes while iterating
    for modname, module in sys.modules.copy().items():
        if ismodule(module) and hasattr(module, '__file__'):
            f = module.__file__
            if f == _filesbymodname.get(modname, None):
                # Have already mapped this module, so skip it
                continue
            _filesbymodname[modname] = f
            f = getabsfile(module)
            # Always map to the name the module knows itself by
            modulesbyfile[f] = modulesbyfile[
                os.path.realpath(f)] = module.__name__
    if file in modulesbyfile:
        return sys.modules.get(modulesbyfile[file])
    # Check the main module
    main = sys.modules['__main__']
    if not hasattr(object, '__name__'):
        return None
    if hasattr(main, object.__name__):
        mainobject = getattr(main, object.__name__)
        if mainobject is object:
            return main
    # Check builtins
    builtin = sys.modules['builtins']
    if hasattr(builtin, object.__name__):
        builtinobject = getattr(builtin, object.__name__)
        if builtinobject is object:
            return builtin


def getsourcefile(object):
    """Return the filename that can be used to locate an object's source.
    Return None if no way can be identified to get the source.
    """
    filename = getfile(object)
    all_bytecode_suffixes = importlib.machinery.DEBUG_BYTECODE_SUFFIXES[:]
    all_bytecode_suffixes += importlib.machinery.OPTIMIZED_BYTECODE_SUFFIXES[:]
    if any(filename.endswith(s) for s in all_bytecode_suffixes):
        filename = (os.path.splitext(filename)[0] +
                    importlib.machinery.SOURCE_SUFFIXES[0])
    elif any(filename.endswith(s) for s in
             importlib.machinery.EXTENSION_SUFFIXES):
        return None
    if os.path.exists(filename):
        return filename
    # only return a non-existent filename if the module has a PEP 302 loader
    if getattr(getmodule(object, filename), '__loader__', None) is not None:
        return filename
    # or it is in the linecache
    if filename in linecache.cache:
        return filename


def getcallargs(func, *positional, **named):
    f_name: str
    # noinspection PyUnresolvedReferences
    assigned_tuple_params: cython.list
    # noinspection PyUnresolvedReferences
    arg2dict: cython.dict
    # noinspection PyUnresolvedReferences
    num_args: cython.int
    # noinspection PyUnresolvedReferences
    num_pos: cython.int
    # noinspection PyUnresolvedReferences
    num_total: cython.int
    # noinspection PyUnresolvedReferences
    num_defaults: cython.int
    # noinspection PyUnresolvedReferences
    num_required: cython.int
    """Get the mapping of arguments to values.

    A dict is returned, with keys the function argument names (including the
    names of the * and ** arguments, if any), and values the respective bound
    values from 'positional' and 'named'.
    """
    args, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, annotations = getfullargspec(func)

    if kwonlyargs:
        raise ValueError("I'm sorry, I don't have the logic to use kwonlyargs. "
                         "Perhapse you can help PyContracts and implement this? Thanks.")

    f_name = func.__name__
    arg2value = {}

    # The following closures are basically because of tuple
    # parameter unpacking.
    assigned_tuple_params = []

    def assign(arg, value):
        # noinspection PyUnresolvedReferences
        arg: cython.p_char
        # noinspection PyUnresolvedReferences
        i: cython.int
        nonlocal assigned_tuple_params
        if isinstance(arg, str):
            arg2value[arg] = value
        else:
            assigned_tuple_params.append(arg)
            value = iter(value)
            for i, subarg in enumerate(arg):
                try:
                    subvalue = next(value)
                except StopIteration:
                    raise ValueError('need more than %d %s to unpack' %
                                     (i, 'values' if i > 1 else 'value'))
                assign(subarg, subvalue)
            try:
                next(value)
            except StopIteration:
                pass
            else:
                raise ValueError('too many values to unpack')

    def is_assigned(arg):
        if isinstance(arg, str):
            return arg in arg2value
        return arg in assigned_tuple_params

    im_self = getattr(func, '__self__', None)

    if ismethod(func) and im_self is not None:
        # implicit 'self' (or 'cls' for classmethods) argument
        positional = (im_self,) + positional
    num_pos = len(positional)
    num_total = num_pos + len(named)
    num_args = len(args)
    num_defaults = len(defaults) if defaults else 0
    for arg, value in zip(args, positional):
        assign(arg, value)
    if varargs:
        if num_pos > num_args:
            assign(varargs, positional[-(num_pos - num_args):])
        else:
            assign(varargs, ())
    elif 0 < num_args < num_pos:
        raise TypeError('%s() takes %s %d %s (%d given)' % (
            f_name, 'at most' if defaults else 'exactly', num_args,
            'arguments' if num_args > 1 else 'argument', num_total))
    elif num_args == 0 and num_total:
        raise TypeError('%s() takes no arguments (%d given)' %
                        (f_name, num_total))
    for arg in args:
        if isinstance(arg, str) and arg in named:
            if is_assigned(arg):
                raise TypeError("%s() got multiple values for keyword "
                                "argument '%s'" % (f_name, arg))
            else:
                assign(arg, named.pop(arg))
    if defaults:  # fill in any missing values with the defaults
        for arg, value in zip(args[-num_defaults:], defaults):
            if not is_assigned(arg):
                assign(arg, value)
    if varkw:
        assign(varkw, named)
    elif named:
        unexpected = next(iter(named))
        if isinstance(unexpected, str):
            unexpected = unexpected.encode(sys.getdefaultencoding(), 'replace')
        raise TypeError("%s() got an unexpected keyword argument '%s'" %
                        (f_name, unexpected))
    unassigned = num_args - len([arg for arg in args if is_assigned(arg)])
    if unassigned:
        num_required = num_args - num_defaults
        raise TypeError('%s() takes %s %d %s (%d given)' % (
            f_name, 'at least' if defaults else 'exactly', num_required,
            'arguments' if num_required > 1 else 'argument', num_total))
    return arg2value


ArgSpec = namedtuple('ArgSpec', 'args varargs keywords defaults')


def getargspec(func):
    """Get the names and default values of a function's parameters.

    A tuple of four things is returned: (args, varargs, keywords, defaults).
    'args' is a list of the argument names, including keyword-only argument names.
    'varargs' and 'keywords' are the names of the * and ** parameters or None.
    'defaults' is an n-tuple of the default values of the last n parameters.

    This function is deprecated, as it does not support annotations or
    keyword-only parameters and will raise ValueError if either is present
    on the supplied callable.

    For a more structured introspection API, use inspect.signature() instead.

    Alternatively, use getfullargspec() for an API with a similar namedtuple
    based interface, but full support for annotations and keyword-only
    parameters.

    Deprecated since Python 3.5, use `inspect.getfullargspec()`.
    """
    warnings.warn("inspect.getargspec() is deprecated since Python 3.0, "
                  "use inspect.signature() or inspect.getfullargspec()",
                  DeprecationWarning, stacklevel=2)
    args, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, ann = \
        getfullargspec(func)
    if kwonlyargs or ann:
        raise ValueError("Function has keyword-only parameters or annotations"
                         ", use inspect.signature() API which can support them")
    return ArgSpec(args, varargs, varkw, defaults)


FullArgSpec = namedtuple('FullArgSpec', 'args, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, annotations')

ArgInfo = namedtuple('ArgInfo', 'args varargs keywords locals')


def formatannotation(annotation, base_module=None):
    if getattr(annotation, '__module__', None) == 'typing':
        return repr(annotation).replace('typing.', '')
    if isinstance(annotation, type):
        if annotation.__module__ in ('builtins', base_module):
            return annotation.__qualname__
        return annotation.__module__ + '.' + annotation.__qualname__
    return repr(annotation)


Traceback = namedtuple('Traceback', 'filename lineno function code_context index')


class ClassFoundException(Exception):
    pass


class _ClassFinder(ast.NodeVisitor):

    def __init__(self, qualname):
        self.stack = []
        self.qualname = qualname

    def visit_FunctionDef(self, node):
        self.stack.append(node.name)
        self.stack.append('<locals>')
        self.generic_visit(node)
        self.stack.pop()
        self.stack.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node):
        self.stack.append(node.name)
        if self.qualname == '.'.join(self.stack):
            # Return the decorator for the class if present
            if node.decorator_list:
                line_number = node.decorator_list[0].lineno
            else:
                line_number = node.lineno

            # decrement by one since lines starts with indexing by zero
            line_number -= 1
            raise ClassFoundException(line_number)
        self.generic_visit(node)
        self.stack.pop()


def findsource(object):
    """Return the entire source file and starting line number for an object.

    The argument may be a module, class, method, function, traceback, frame,
    or code object.  The source code is returned as a list of all the lines
    in the file and the line number indexes a line in that list.  An OSError
    is raised if the source code cannot be retrieved."""

    file = getsourcefile(object)
    if file:
        # Invalidate cache if needed.
        linecache.checkcache(file)
    else:
        file = getfile(object)
        # Allow filenames in form of "<something>" to pass through.
        # `doctest` monkeypatches `linecache` module to enable
        # inspection, so let `linecache.getlines` to be called.
        if not (file.startswith('<') and file.endswith('>')):
            raise OSError('source code not available')

    module = getmodule(object, file)
    if module:
        lines = linecache.getlines(file, module.__dict__)
    else:
        lines = linecache.getlines(file)
    if not lines:
        raise OSError('could not get source code')

    if ismodule(object):
        return lines, 0

    if isclass(object):
        qualname = object.__qualname__
        source = ''.join(lines)
        tree = ast.parse(source)
        class_finder = _ClassFinder(qualname)
        try:
            class_finder.visit(tree)
        except ClassFoundException as e:
            line_number = e.args[0]
            return lines, line_number
        else:
            raise OSError('could not find class definition')

    if ismethod(object):
        object = object.__func__
    if isfunction(object):
        object = object.__code__
    if istraceback(object):
        object = object.tb_frame
    if isframe(object):
        object = object.f_code
    if iscode(object):
        if not hasattr(object, 'co_firstlineno'):
            raise OSError('could not find function definition')
        lnum = object.co_firstlineno - 1
        pat = re.compile(r'^(\s*def\s)|(\s*async\s+def\s)|(.*(?<!\w)lambda(:|\s))|^(\s*@)')
        while lnum > 0:
            try:
                line = lines[lnum]
            except IndexError:
                raise OSError('lineno is out of bounds')
            if pat.match(line):
                break
            lnum = lnum - 1
        return lines, lnum
    raise OSError('could not find code object')


def getframeinfo(frame, context=1):
    """Get information about a frame or traceback object.

    A tuple of five things is returned: the filename, the line number of
    the current line, the function name, a list of lines of context from
    the source code, and the index of the current line within that list.
    The optional second argument specifies the number of lines of context
    to return, which are centered around the current line."""
    if istraceback(frame):
        lineno = frame.tb_lineno
        frame = frame.tb_frame
    else:
        lineno = frame.f_lineno
    if not isframe(frame):
        raise TypeError('{!r} is not a frame or traceback object'.format(frame))

    filename = getsourcefile(frame) or getfile(frame)
    if context > 0:
        start = lineno - 1 - context // 2
        try:
            lines, lnum = findsource(frame)
        except OSError:
            lines = index = None
        else:
            start = max(0, min(start, len(lines) - context))
            lines = lines[start:start + context]
            index = lineno - 1 - start
    else:
        lines = index = None

    return Traceback(filename, lineno, frame.f_code.co_name, lines, index)


def getlineno(frame):
    """Get the line number from a frame object, allowing for optimization."""
    # FrameType.f_lineno is now a descriptor that grovels co_lnotab
    return frame.f_lineno


FrameInfo = namedtuple('FrameInfo', ('frame',) + Traceback._fields)


def getouterframes(frame, context=1):
    """Get a list of records for a frame and all higher (calling) frames.

    Each record contains a frame object, filename, line number, function
    name, a list of lines of context, and index within the context."""
    framelist = []
    while frame:
        frameinfo = (frame,) + getframeinfo(frame, context)
        framelist.append(FrameInfo(*frameinfo))
        frame = frame.f_back
    return framelist


def getinnerframes(tb, context=1):
    """Get a list of records for a traceback's frame and all lower frames.

    Each record contains a frame object, filename, line number, function
    name, a list of lines of context, and index within the context."""
    framelist = []
    while tb:
        frameinfo = (tb.tb_frame,) + getframeinfo(tb, context)
        framelist.append(FrameInfo(*frameinfo))
        tb = tb.tb_next
    return framelist


def currentframe():
    """Return the frame of the caller or None if this is not possible."""
    return sys._getframe(1) if hasattr(sys, "_getframe") else None


def stack(context=1):
    """Return a list of records for the stack above the caller's frame."""
    # noinspection PyProtectedMember, PyUnresolvedReferences
    return getouterframes(sys._getframe(1), context)


def trace(context=1):
    """Return a list of records for the stack below the current exception."""
    # noinspection PyTypeChecker
    return getinnerframes(sys.exc_info()[2], context)


class _void:
    """A private marker - used in Parameter & Signature."""


class _empty:
    """Marker object for Signature.empty and Parameter.empty."""


class _ParameterKind(enum.IntEnum):
    POSITIONAL_ONLY = 0
    POSITIONAL_OR_KEYWORD = 1
    VAR_POSITIONAL = 2
    KEYWORD_ONLY = 3
    VAR_KEYWORD = 4

    def __str__(self):
        return self._name_

    @property
    def description(self):
        return _PARAM_NAME_MAPPING[self]


_POSITIONAL_ONLY = _ParameterKind.POSITIONAL_ONLY
_POSITIONAL_OR_KEYWORD = _ParameterKind.POSITIONAL_OR_KEYWORD
_VAR_POSITIONAL = _ParameterKind.VAR_POSITIONAL
_KEYWORD_ONLY = _ParameterKind.KEYWORD_ONLY
_VAR_KEYWORD = _ParameterKind.VAR_KEYWORD

_PARAM_NAME_MAPPING = {
    _POSITIONAL_ONLY: 'positional-only',
    _POSITIONAL_OR_KEYWORD: 'positional or keyword',
    _VAR_POSITIONAL: 'variadic positional',
    _KEYWORD_ONLY: 'keyword-only',
    _VAR_KEYWORD: 'variadic keyword'
}


class Parameter:
    """Represents a parameter in a function signature.

    Has the following public attributes:

    * name : str
        The name of the parameter as a string.
    * default : object
        The default value for the parameter if specified.  If the
        parameter has no default value, this attribute is set to
        `Parameter.empty`.
    * annotation
        The annotation for the parameter if specified.  If the
        parameter has no annotation, this attribute is set to
        `Parameter.empty`.
    * kind : str
        Describes how argument values are bound to the parameter.
        Possible values: `Parameter.POSITIONAL_ONLY`,
        `Parameter.POSITIONAL_OR_KEYWORD`, `Parameter.VAR_POSITIONAL`,
        `Parameter.KEYWORD_ONLY`, `Parameter.VAR_KEYWORD`.
    """

    __slots__ = ('_name', '_kind', '_default', '_annotation')

    POSITIONAL_ONLY = _POSITIONAL_ONLY
    POSITIONAL_OR_KEYWORD = _POSITIONAL_OR_KEYWORD
    VAR_POSITIONAL = _VAR_POSITIONAL
    KEYWORD_ONLY = _KEYWORD_ONLY
    VAR_KEYWORD = _VAR_KEYWORD

    empty = _empty

    def __init__(self, name, kind, *, default=_empty, annotation=_empty):
        try:
            self._kind = _ParameterKind(kind)
        except ValueError:
            raise ValueError(f'value {kind!r} is not a valid Parameter.kind')
        if default is not _empty:
            if self._kind in (_VAR_POSITIONAL, _VAR_KEYWORD):
                msg = '{} parameters cannot have default values'
                msg = msg.format(self._kind.description)
                raise ValueError(msg)
        self._default = default
        self._annotation = annotation

        if name is _empty:
            raise ValueError('name is a required attribute for Parameter')

        if not isinstance(name, str):
            msg = 'name must be a str, not a {}'.format(type(name).__name__)
            raise TypeError(msg)

        if name[0] == '.' and name[1:].isdigit():
            # These are implicit arguments generated by comprehensions. In
            # order to provide a friendlier interface to users, we recast
            # their name as "implicitN" and treat them as positional-only.
            # See issue 19611.
            if self._kind != _POSITIONAL_OR_KEYWORD:
                msg = (
                    'implicit arguments must be passed as '
                    'positional or keyword arguments, not {}'
                )
                msg = msg.format(self._kind.description)
                raise ValueError(msg)
            self._kind = _POSITIONAL_ONLY
            name = 'implicit{}'.format(name[1:])

        if not name.isidentifier():
            raise ValueError('{!r} is not a valid parameter name'.format(name))

        self._name = name

    def __reduce__(self):
        return (type(self),
                (self._name, self._kind),
                {'_default': self._default,
                 '_annotation': self._annotation})

    def __setstate__(self, state):
        self._default = state['_default']
        self._annotation = state['_annotation']

    @property
    def name(self):
        return self._name

    @property
    def default(self):
        return self._default

    @property
    def annotation(self):
        return self._annotation

    @property
    def kind(self):
        return self._kind

    def replace(self, *, name=_void, kind=_void,
                annotation=_void, default=_void):
        """Creates a customized copy of the Parameter."""

        if name is _void:
            name = self._name

        if kind is _void:
            kind = self._kind

        if annotation is _void:
            annotation = self._annotation

        if default is _void:
            default = self._default

        return type(self)(name, kind, default=default, annotation=annotation)

    def __str__(self):
        kind = self.kind
        formatted = self._name

        # Add annotation and default value
        if self._annotation is not _empty:
            formatted = '{}: {}'.format(formatted,
                                        formatannotation(self._annotation))

        if self._default is not _empty:
            if self._annotation is not _empty:
                formatted = '{} = {}'.format(formatted, repr(self._default))
            else:
                formatted = '{}={}'.format(formatted, repr(self._default))

        if kind == _VAR_POSITIONAL:
            formatted = '*' + formatted
        elif kind == _VAR_KEYWORD:
            formatted = '**' + formatted

        return formatted

    def __repr__(self):
        return '<{} "{}">'.format(self.__class__.__name__, self)

    def __hash__(self):
        return hash((self.name, self.kind, self.annotation, self.default))

    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, Parameter):
            return NotImplemented
        return (self._name == other._name and
                self._kind == other._kind and
                self._default == other._default and
                self._annotation == other._annotation)


class BoundArguments:
    """Result of `Signature.bind` call.  Holds the mapping of arguments
    to the function's parameters.

    Has the following public attributes:

    * arguments : dict
        An ordered mutable mapping of parameters' names to arguments' values.
        Does not contain arguments' default values.
    * signature : Signature
        The Signature object that created this instance.
    * args : tuple
        Tuple of positional arguments values.
    * kwargs : dict
        Dict of keyword arguments values.
    """

    __slots__ = ('arguments', '_signature', '__weakref__')

    def __init__(self, signature, arguments):
        self.arguments = arguments
        self._signature = signature

    @property
    def signature(self):
        return self._signature

    @property
    def args(self):
        args = []
        for param_name, param in self._signature.parameters.items():
            if param.kind in (_VAR_KEYWORD, _KEYWORD_ONLY):
                break

            try:
                arg = self.arguments[param_name]
            except KeyError:
                # We're done here. Other arguments
                # will be mapped in 'BoundArguments.kwargs'
                break
            else:
                if param.kind == _VAR_POSITIONAL:
                    # *args
                    args.extend(arg)
                else:
                    # plain argument
                    args.append(arg)

        return tuple(args)

    @property
    def kwargs(self):
        kwargs = {}
        kwargs_started = False
        for param_name, param in self._signature.parameters.items():
            if not kwargs_started:
                if param.kind in (_VAR_KEYWORD, _KEYWORD_ONLY):
                    kwargs_started = True
                else:
                    if param_name not in self.arguments:
                        kwargs_started = True
                        continue

            if not kwargs_started:
                continue

            try:
                arg = self.arguments[param_name]
            except KeyError:
                pass
            else:
                if param.kind == _VAR_KEYWORD:
                    # **kwargs
                    kwargs.update(arg)
                else:
                    # plain keyword argument
                    kwargs[param_name] = arg

        return kwargs

    def apply_defaults(self):
        """Set default values for missing arguments.

        For variable-positional arguments (*args) the default is an
        empty tuple.

        For variable-keyword arguments (**kwargs) the default is an
        empty dict.
        """
        arguments = self.arguments
        new_arguments = []
        for name, param in self._signature.parameters.items():
            try:
                new_arguments.append((name, arguments[name]))
            except KeyError:
                if param.default is not _empty:
                    val = param.default
                elif param.kind is _VAR_POSITIONAL:
                    val = ()
                elif param.kind is _VAR_KEYWORD:
                    val = {}
                else:
                    # This BoundArguments was likely produced by
                    # Signature.bind_partial().
                    continue
                new_arguments.append((name, val))
        self.arguments = dict(new_arguments)

    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, BoundArguments):
            return NotImplemented
        return (self.signature == other.signature and
                self.arguments == other.arguments)

    def __setstate__(self, state):
        self._signature = state['_signature']
        self.arguments = state['arguments']

    def __getstate__(self):
        return {'_signature': self._signature, 'arguments': self.arguments}

    def __repr__(self):
        args = []
        for arg, value in self.arguments.items():
            args.append('{}={!r}'.format(arg, value))
        return '<{} ({})>'.format(self.__class__.__name__, ', '.join(args))


def can_accept_exactly_one_argument(callable_thing):
    """ Checks that a callable can accept exactly one argument
        using introspection.
    """
    if ismethod(callable_thing):  # bound method
        f = callable_thing.__func__
        args = (callable_thing.__self__, 'test',)
    else:
        if not isfunction(callable_thing):
            f = callable_thing.__call__
        else:
            f = callable_thing
        args = ('test',)

    try:
        getcallargs(f, *args)
    except (TypeError, ValueError) as e:  # @UnusedVariable
        # print 'Get call args exception (f=%r,args=%r): %s ' % (f, args, e)
        return False, str(e)
    else:
        return True, None


def get_f_from_callable(callable_thing):
    if ismethod(callable_thing):  # bound method
        f = callable_thing.__func__
        # args = (callable_thing.__self__, 'test',)
    else:
        if not isfunction(callable_thing):
            f = callable_thing.__call__
        else:
            f = callable_thing
            # args = ('test',)
    return f


def get_callable_fullargspec(callable_thing):
    f: Callable
    spec: FullArgSpec
    f = get_f_from_callable(callable_thing)
    spec = getfullargspec(f)
    return spec


def can_accept_at_least_one_argument(callable_thing):
    """ 
        Checks that a callable can accept at least one argument
        using introspection.
    """
    spec = get_callable_fullargspec(callable_thing)
    return len(spec.args) > 0 or spec.varargs


def can_accept_self(callable_thing):
    """ 
        Checks that a callable's first argument is self
    """
    spec = get_callable_fullargspec(callable_thing)

    if len(spec.args) == 0 or spec.args[0] != 'self':
        return False

    return True


def can_accept_self_plus_one_argument(callable_thing):
    """ 
        Checks that a callable can accept exactly self plus one argument
        using introspection.
    """

    spec = get_callable_fullargspec(callable_thing)
    if len(spec.args) == 0 or spec.args[0] != 'self':
        return False

    f = get_f_from_callable(callable_thing)
    try:
        getcallargs(f, 'self', 'value')
    except (TypeError, ValueError) as e:  # @UnusedVariable
        return False
    else:
        return True


class InvalidArgs(Exception):
    pass


def check_callable_accepts_these_arguments(callable_thing, args, kwargs):
    """ Checks that a callable can accept the args and kwargs. 
    
        Returns either None or raises InvalidArgs. 
    """
    f = get_f_from_callable(callable_thing)

    try:
        getcallargs(f, *args, **kwargs)
    except Exception as e:
        raise InvalidArgs('%s does not accept %s, %s: %s' % (f, args, kwargs, e))
    else:
        return True
