import warnings

from contracts import describe_value, describe_type


__all__ = [
   'indent',
   'deprecated',
   'raise_type_mismatch',
]

def indent(s, prefix):
    lines = s.split('\n')
    lines = ['%s%s' % (prefix, line.rstrip()) for line in lines]
    return '\n'.join(lines)


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
    e +='\n  expected: %s' % expected
    e +='\n  obtained: %s' % type(ob)
    e += '\n' + indent(format_obs(kwargs), ' ')
    raise ValueError(e)


def format_obs(d):
    """ Shows objects values and typed for the given dictionary """
    lines = []
    for name, value in d.items():
        lines.append('%15s: %s' % (name, describe_value(value)))
        lines.append('%15s  %s' % ('of type', describe_type(value)))
    return '\n'.join(lines)

