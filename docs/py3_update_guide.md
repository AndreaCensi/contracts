# PyContracts Python 3 Compatibility Guide

This guide explains how to update your PyContracts-using codebase to
work with Python 3, particularly Python 3.12+ which removes collection
ABC classes from the `collections` module.

## Background

The PyContracts library was originally designed for Python 2, and
while it has some support for Python 3, it needs additional
compatibility fixes for Python 3.12+ which removed several collection
classes from the `collections` module and moved them to
`collections.abc`.

## Option 1: Use Our Patched Version

The easiest option is to use our patched version of PyContracts:

1. Clone this repository to a directory in your Python path
3. Make sure to add `past` to your requirements if you need Python 2 compatibility

## Option 2: Create a Compatibility Layer

If you want to patch your existing PyContracts installation:

1. Create a compatibility module (`py_compatibility.py`) with the following content:

```python
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
else:
    # Python 2
    exec("""def reraise(exception, traceback=None):
        if traceback is None:
            raise exception
        else:
            raise exception, None, traceback
    """)

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
```

2. Update the collection imports in the following files:
   - `library/seq.py`
   - `library/map.py`
   - `library/sets.py`

3. Replace six reference with your compatibility module:
   - In `interface.py`
   - In `utils.py`

4. Add xrange compatibility in `seq.py`:
```python
# Use range across Python 2/3
try:
    from past.builtins import xrange
except ImportError:
    xrange = range
```

5. Fix the exception handling in `utils.py`:
```python
def raise_wrapped(etype, e, msg, compact=False, **kwargs):
    if PY3:
        msg += '\n' + indent(str(e), '| ')
        e2 = etype(_format_exc(msg, **kwargs))
        reraise(e2, e.__traceback__)
    else:
        e2 = raise_wrapped_make(etype, e, msg, compact=compact, **kwargs)
        reraise(e2)
```

## Option 3: Update Your Code to Avoid Problematic Contracts

If you can't modify the PyContracts library, update your code to avoid contracts that use problematic collection types:

1. Instead of:
```python
@contract(x='set')
def my_function(x):
    ...
```

2. Use:
```python
@contract(x='isinstance(x, collections.abc.Set)')
def my_function(x):
    ...
```

This approach uses raw predicates instead of the built-in contract
types, which will avoid the collection type issues.

## Testing

You can use the provided test script `test_pycontracts_py3.py` to
verify your PyContracts changes:

```bash
python test_pycontracts_py3.py
```

This script will test basic contracts, collection type contracts, custom contracts, and exception handling to ensure everything works correctly.

## Common Issues and Solutions

1. **ImportError from collections module**:
   - Error: `ImportError: cannot import name 'Sequence' from 'collections'`
   - Solution: Use the compatibility layer that imports from collections.abc

2. **StringIO compatibility issues**:
   - Error: `ImportError: No module named StringIO`
   - Solution: Use the compatibility layer for StringIO/BytesIO

3. **xrange not defined in Python 3**:
   - Error: `NameError: name 'xrange' is not defined`
   - Solution: Add the xrange compatibility shim

4. **String type checking errors**:
   - Error: `TypeError: isinstance() arg 2 must be a type or tuple of types`
   - Solution: Use the string_types compatibility constant

Goodluck!