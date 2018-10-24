# -*- coding: utf-8 -*-
import traceback
import warnings

from .interface import describe_type, describe_value  # @UnusedImport # old interface

__all__ = [
    'indent',
    'deprecated',
    'raise_type_mismatch',
    'raise_wrapped',
    'raise_desc',
    'check_isinstance',
]


def indent(s, prefix, first=None):
    s = str(s)
    assert isinstance(prefix, str)
    lines = s.split('\n')
    if not lines:
        return ''

    if first is None:
        first = prefix

    m = max(len(prefix), len(first))

    prefix = ' ' * (m - len(prefix)) + prefix
    first = ' ' * (m - len(first)) + first

    # differnet first prefix
    res = ['%s%s' % (prefix, line.rstrip()) for line in lines]
    res[0] = '%s%s' % (first, lines[0].rstrip())
    return '\n'.join(res)


def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used."""

    def new_func(*args, **kwargs):
        warnings.warn("Call to deprecated function %s." % func.__name__,
                      category=DeprecationWarning, stacklevel=2)
        return func(*args, **kwargs)

    new_func.__name__ = func.__name__
    new_func.__doc__ = func.__doc__
    new_func.__dict__.update(func.__dict__)
    return new_func


def check_isinstance(ob, expected, **kwargs):
    if not isinstance(ob, expected):
        kwargs['object'] = ob
        raise_type_mismatch(ob, expected, **kwargs)


def raise_type_mismatch(ob, expected, **kwargs):
    """ Raises an exception concerning ob having the wrong type. """
    e = 'Object not of expected type:'
    e += '\n  expected: %s' % str(expected)
    e += '\n  obtained: %s' % str(type(ob))
    e += '\n' + indent(format_obs(kwargs), ' ')
    raise ValueError(e)


def format_dict_long(d, informal=False):
    """
        k: value
           kooked
        k: value
    """
    if not d:
        return '{}'

    maxlen = max([len(n) for n in d]) + 2

    def pad(pre):
        return ' ' * (maxlen - len(pre)) + pre

    res = ""
    order = sorted(d)
    for i, name in enumerate(order):
        value = d[name]
        prefix = pad('%s: ' % name)
        if i > 0:
            res += '\n'

        s = _get_str(value, informal)

        if len(s) > 512:
            s = s[:512] + ' [truncated]'
        res += indent(s, ' ', first=prefix)
    return res


def _get_str(x, informal):
    from contracts.interface import describe_value_multiline
    if informal:
        s = str(x)
    else:
        s = describe_value_multiline(x)
    return s


def format_list_long(l, informal=False):
    """
        - My 
          first
        - Second
    """
    res = ""
    for i, value in enumerate(l):
        prefix = '- '
        if i > 0:
            res += '\n'
        s = _get_str(value, informal)
        res += indent(s, ' ', first=prefix)
    return res


def format_obs(d, informal=False):
    """ Shows objects values and typed for the given dictionary """
    if not d:
        return str(d)

    maxlen = 0
    for name in d:
        maxlen = max(len(name), maxlen)

    def pad(pre):
        return ' ' * (maxlen - len(pre)) + pre

    res = ''

    S = sorted(d)
    for i, name in enumerate(S):
        value = d[name]
        prefix = pad('%s: ' % name)
        if i > 0:
            res += '\n'

        s = _get_str(value, informal)

        res += indent(s, ' ', first=prefix)

    return res


def raise_wrapped(etype, e, msg, compact=False, exc=None, **kwargs):
    """ Raises an exception of type etype by wrapping
        another exception "e" with its backtrace and adding
        the objects in kwargs as formatted by format_obs.
        
        if compact = False, write the whole traceback, otherwise just str(e).
    
        exc = output of sys.exc_info()
    """

    e = raise_wrapped_make(etype, e, msg, compact=compact, **kwargs)

    #     if exc is not None:
    #         _, _, trace = exc
    #         raise etype, e.args, trace
    #     else:
    raise e


def raise_wrapped_make(etype, e, msg, compact=False, **kwargs):
    """ Constructs the exception to be thrown by raise_wrapped() """
    assert isinstance(e, BaseException), type(e)
    assert isinstance(msg, str), type(msg)
    s = msg
    if kwargs:
        s += '\n' + format_obs(kwargs)

    import sys
    if sys.version_info[0] >= 3:
        es = str(e)
    else:
        if compact:
            es = str(e)
        else:
            es = traceback.format_exc(e) # only PY2

    s += '\n' + indent(es.strip(), '| ')

    return etype(s)


def raise_desc(etype, msg, args_first=False, **kwargs):
    """
    
        Example:
            raise_desc(ValueError, "I don't know", a=a, b=b)
    """
    assert isinstance(msg, str), type(msg)
    s1 = msg
    if kwargs:
        s2 = format_obs(kwargs)
    else:
        s2 = ""

    if args_first:
        s = s2 + "\n" + s1
    else:
        s = s1 + "\n" + s2

    raise etype(s)


#
#
#
# def format_tb(tb, limit = None):
#     """A shorthand for 'format_list(extract_stack(f, limit))."""
#     return format_list(extract_tb(tb, limit))
#
# def extract_tb(tb, limit = None):
#     """Return list of up to limit pre-processed entries from traceback.
#
#     This is useful for alternate formatting of stack traces.  If
#     'limit' is omitted or None, all entries are extracted.  A
#     pre-processed stack trace entry is a quadruple (filename, line
#     number, function name, text) representing the information that is
#     usually printed for a stack trace.  The text is a string with
#     leading and trailing whitespace stripped; if the source is not
#     available it is None.
#     """
#     if limit is None:
#         if hasattr(sys, 'tracebacklimit'):
#             limit = sys.tracebacklimit
#     list = []
#     n = 0
#     while tb is not None and (limit is None or n < limit):
#         f = tb.tb_frame
#         lineno = tb.tb_lineno
#         co = f.f_code
#         filename = co.co_filename
#         name = co.co_name
#         linecache.checkcache(filename)
#         line = linecache.getline(filename, lineno, f.f_globals)
#         if line: line = line.strip()
#         else: line = None
#         list.append((filename, lineno, name, line))
#         tb = tb.tb_next
#         n = n+1
#     return list


# from decorator import decorator  # @UnresolvedImport

def ignore_typeerror(f):
    """ Recasts TypeError as Exception; otherwise pyparsing gets confused. """

    def f2(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except TypeError as e:
            raise Exception(traceback.format_exc())

    return f2
