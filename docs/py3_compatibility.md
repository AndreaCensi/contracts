# PyContracts Python 3 Compatibility Changes

This document outlines the changes made to make the PyContracts module
compatible with Python 3, particularly Python 3.12+ which removed
collection ABC classes from the `collections` module.

## 0. Updated String Handling

Modified string type checks:
- Replaced `six.string_types` with our compatibility `string_types`
- Replaced `six.text_type` with our compatibility `text_type`
- Updated string handling in `Where` class in `interface.py`
- Fixed `printable_length_where` to properly handle Python 3 strings

## 1. Fixed Collections ABC Imports

Updated the collection imports in:
- `seq.py`
- `map.py`
- `sets.py`

## 2. Created Compatibility Layer

Created a new module `py_compatibility.py` that provides:
- String type compatibility (`string_types`, `text_type`, `binary_type`)
- Collections module compatibility (for Python 3.12+)
- StringIO compatibility
- Exception handling (reraise) compatibility
- Python 2/3 detection constants

Using our compatibility layer:
```python
from ..py_compatibility import Sequence, MutableMapping, Mapping, Set, MutableSet
```

Key features

```python
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
    MutableMapping = collections.MutableMapping
    Mapping = collections.Mapping
    Set = collections.Set
    MutableSet = collections.MutableSet
    Iterable = collections.Iterable
    Container = collections.Container
    Sized = collections.Sized

# Exception handling compatibility
def reraise(exception, traceback=None):
    # Python 3/2 compatible exception re-raising
    ...
```

## 3. Fixed Exception Handling

1. Added exception handling utilities in `py_compatibility.py`:
```python
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
    # Python 2 equivalent implementations
```

2. Updated the `raise_wrapped` function in `utils.py`:
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

3. Enhanced the Contract's `check` method to properly wrap all exceptions:
```python
def check(self, value):
    """Checks that the value satisfies this contract."""
    def check_func():
        return self.check_contract({}, value, silent=False)
    
    def create_exception(msg):
        return ContractNotRespected(self, msg, value, {})
        
    return catch_and_wrap(check_func, Exception, create_exception)
```

4. Updated `eval_in_context` for better exception handling:
```python
def eval_in_context(context, value, contract):
    def evaluate():
        return value.eval(context)
    
    def create_message(e):
        return 'Error while evaluating RValue %r: %s' % (value, e)
    
    def create_exception(msg):
        return ContractNotRespected(contract, msg, value, context)
    
    return catch_and_wrap(evaluate, ValueError, create_exception, create_message)
```

## 4. Fixed Python 2 Class Type Checking

Updated the `describe_type` function in `interface.py` to check for old-style classes in Python 2:
```python
def describe_type(x):
    if not PY3 and isinstance(x, ClassType):
        class_name = '(old-style class) %s' % x
    else:
        # Normal class handling
```

## 5. xrange Compatibility

Added compatibility for xrange:
```python
# Use range across Python 2/3
try:
    from past.builtins import xrange
except ImportError:
    xrange = range
```

## 6. Removed six Dependency

Replaced all six references with our own compatibility functions:
- Removed imports of the six module
- Used our own string type checks
- Used our own Python version detection

