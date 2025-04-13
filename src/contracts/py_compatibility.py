"""
Compatibility utilities for PyContracts to work with both Python 2 and 3.
"""
import sys
import collections

# Python 2/3 string/bytes compatibility
PY3 = sys.version_info[0] >= 3
PY3_12_PLUS = sys.version_info >= (3, 12)

# String types compatibility
if PY3:
    string_types = (str,)
    text_type = str
    binary_type = bytes
else:
    string_types = (basestring,)
    text_type = unicode
    binary_type = str

# Collection ABC types compatibility
try:
    # Python 3.12+ removed these from collections
    from collections.abc import (
        Sequence, MutableSequence, 
        Mapping, MutableMapping,
        Set, MutableSet,
        Iterable, Container, Sized
    )
except ImportError:
    # Python 2 compatibility
    Sequence = collections.Sequence
    MutableSequence = collections.MutableSequence
    Mapping = collections.Mapping
    MutableMapping = collections.MutableMapping
    Set = collections.Set
    MutableSet = collections.MutableSet
    Iterable = collections.Iterable
    Container = collections.Container
    Sized = collections.Sized

# StringIO compatibility
try:
    from io import StringIO, BytesIO
except ImportError:
    # Python 2
    from StringIO import StringIO
    from cStringIO import StringIO as BytesIO

# Exception handling compatibility
if PY3:
    def reraise(exception, traceback=None):
        """Re-raise exception with optional traceback in Python 3."""
        if traceback is not None and exception.__traceback__ is not traceback:
            raise exception.with_traceback(traceback)
        raise exception
        
    def catch_and_wrap(func, exceptions, wrapper_exception, msg_func=None):
        """Catch exceptions and wrap them in Python 3."""
        try:
            return func()
        except exceptions as e:
            if msg_func:
                msg = msg_func(e)
            else:
                msg = str(e)
            wrapped = wrapper_exception(msg)
            raise wrapped from e
else:
    # Python 2
    exec("""def reraise(exception, traceback=None):
        if traceback is None:
            raise exception
        else:
            raise exception, None, traceback
    """)
    
    def catch_and_wrap(func, exceptions, wrapper_exception, msg_func=None):
        """Catch exceptions and wrap them in Python 2."""
        try:
            return func()
        except exceptions as e:
            if msg_func:
                msg = msg_func(e)
            else:
                msg = str(e)
            wrapped = wrapper_exception(msg)
            reraise(wrapped)
    

# Print function compatibility for Python 2
if not PY3:
    # These are needed for Python 2
    import copy_reg
    import types
    
    def _reduce_method(m):
        """Helper function for Python 2 pickling of methods."""
        if m.__self__ is None:
            return getattr, (m.__self__.__class__, m.__func__.__name__)
        else:
            return getattr, (m.__self__, m.__func__.__name__)
    
    copy_reg.pickle(types.MethodType, _reduce_method)