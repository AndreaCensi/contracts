import sys
from inspect import ArgSpec

if sys.version_info[0] >= 3:  # pragma: no cover
    from inspect import getfullargspec
    unicode = str

else:  # pragma: no cover
    from collections import namedtuple
    FullArgSpec = namedtuple('FullArgSpec', 'args varargs varkw defaults'
                             ' kwonlyargs kwonlydefaults annotations')
    from inspect import getargspec as _getargspec

    def getargspec(function):
        # print 'hasattr im_func', hasattr(function, 'im_func')
        if hasattr(function, 'im_func'):
            # print('this is a special function : %s' % function)
            # For methods or classmethods drop the first
            # argument from the returned list because
            # python supplies that automatically for us.
            # Note that this differs from what
            # inspect.getargspec() returns for methods.
            # NB: We use im_func so we work with
            #     instancemethod objects also.
            x = _getargspec(function.im_func)
            new_args = x.args[1:]
            spec = ArgSpec(args=new_args, varargs=x.varargs,
                           keywords=x.keywords, defaults=x.defaults)
            return spec

        # print 'calling normal %s' % function
        return _getargspec(function)

    def getfullargspec(function):
        spec = getargspec(function)
        fullspec = FullArgSpec(args=spec.args, varargs=spec.varargs,
                               varkw=spec.keywords,
                               defaults=spec.defaults, kwonlyargs=[],
                               kwonlydefaults=None,
                               annotations={})
        return fullspec


# Backport inspect.getcallargs from Python 2.7 to 2.6
if sys.version_info[:2] == (2, 7):
    # noinspection PyUnresolvedReferences
    from inspect import getcallargs
else:  # pragma: no cover
    inPy3k = sys.version_info[0] == 3

    from inspect import ismethod

    def getcallargs(func, *positional, **named):
        """Get the mapping of arguments to values.

        A dict is returned, with keys the function argument names (including the
        names of the * and ** arguments, if any), and values the respective bound
        values from 'positional' and 'named'.
        """
        args, varargs, varkw, defaults, \
            kwonlyargs, kwonlydefaults, annotations = getfullargspec(func)

        if kwonlyargs:
            raise ValueError("I'm sorry, I don't have the logic to use kwonlyargs. "
                             "Perhapse you can help PyContracts and implement this? Thanks.")

        f_name = func.__name__
        arg2value = {}

        # The following closures are basically because of tuple
        # parameter unpacking.
        assigned_tuple_params = []

        def assign(arg, value):
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

        if not inPy3k:
            im_self = getattr(func, 'im_self', None)
        else:
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
            if isinstance(unexpected, unicode):
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



