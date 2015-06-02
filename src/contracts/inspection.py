import sys
import inspect
from .backported import getcallargs, getfullargspec


inPy2 = sys.version_info[0] == 2
if inPy2:
    from types import ClassType


def can_be_used_as_a_type(x):
    """ Checks that x can be used as a type; specifically,
        we can write isintance(y,x).
        Here we support old-style classes.
    """
    if isinstance(x, type):
        return True

    if inPy2:
        if isinstance(x, ClassType):
            return True

    return False


def can_accept_exactly_one_argument(callable_thing):
    """ Checks that a callable can accept exactly one argument
        using introspection.
    """
    if inspect.ismethod(callable_thing):  # bound method
        f = callable_thing.__func__
        args = (callable_thing.__self__, 'test',)
    else:
        if not inspect.isfunction(callable_thing):
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
    if inspect.ismethod(callable_thing):  # bound method
        f = callable_thing.__func__
        # args = (callable_thing.__self__, 'test',)
    else:
        if not inspect.isfunction(callable_thing):
            f = callable_thing.__call__
        else:
            f = callable_thing
            # args = ('test',)
    return f

def get_callable_fullargspec(callable_thing):
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

    # TODO: redo better
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

    # TODO: more cleanly
    try:
        bound = getcallargs(f, *args, **kwargs)
        # print('bound: %r ' % bound)
    except (TypeError, ValueError) as e:  # @UnusedVariable
        # print('no!: %s' % e)
        raise InvalidArgs('%s does not accept %s, %s: %s' % (f, args, kwargs, e))
        # return False
    else:
        return True

    return False
