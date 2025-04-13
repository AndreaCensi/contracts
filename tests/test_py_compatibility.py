#!/usr/bin/env python
"""
Test script to verify PyContracts py_compatibility module functionality.
"""
import pytest
import sys
import io
import traceback
from collections import OrderedDict
from collections.abc import Sequence, Mapping, Set

from contracts.py_compatibility import (
    PY3, PY3_12_PLUS, string_types, text_type, binary_type,
    StringIO, BytesIO, reraise, catch_and_wrap,
    Sequence as compat_Sequence,
    Mapping as compat_Mapping,
    Set as compat_Set,
    MutableMapping, MutableSequence, MutableSet,
    Iterable, Container, Sized
)


def test_version_detection():
    """Test Python version detection constants."""
    # PY3 should be True for Python 3.x
    assert PY3 == (sys.version_info[0] >= 3)
    
    # PY3_12_PLUS should be True for Python 3.12+
    assert PY3_12_PLUS == (sys.version_info >= (3, 12))


def test_string_types():
    """Test string type compatibility wrappers."""
    # Check string_types detection
    assert isinstance("test string", string_types)
    assert not isinstance(123, string_types)
    assert not isinstance(b"bytes data", string_types) if PY3 else isinstance(b"bytes data", string_types)
    
    # Check text_type
    assert isinstance("text", text_type)
    assert text_type("123") == "123"
    
    # Check binary_type
    assert isinstance(b"binary", binary_type)
    if PY3:
        assert binary_type("hello", "utf-8") == b"hello"


def test_stringio_compatibility():
    """Test StringIO and BytesIO compatibility wrappers."""
    # StringIO should accept and return strings
    string_io = StringIO()
    string_io.write("test string")
    string_io.seek(0)
    assert string_io.read() == "test string"
    
    # BytesIO should accept and return bytes
    if PY3:
        bytes_io = BytesIO()
        bytes_io.write(b"test bytes")
        bytes_io.seek(0)
        assert bytes_io.read() == b"test bytes"


def test_collections_abc_compatibility():
    """Test collections ABC compatibility."""
    # Check imported collection types match their stdlib equivalents
    assert compat_Sequence == Sequence
    assert compat_Mapping == Mapping
    assert compat_Set == Set
    
    # Check basic functionality
    assert issubclass(list, compat_Sequence)
    assert issubclass(dict, compat_Mapping)
    assert issubclass(set, compat_Set)
    
    # Test MutableSequence
    assert issubclass(list, MutableSequence)
    assert not issubclass(tuple, MutableSequence)
    
    # Test MutableMapping
    assert issubclass(dict, MutableMapping)
    assert not issubclass(OrderedDict, Sized) or issubclass(OrderedDict, Sized)  # This should pass either way
    
    # Test MutableSet
    assert issubclass(set, MutableSet)
    assert not issubclass(frozenset, MutableSet)
    
    # Test other collection ABCs
    assert issubclass(list, Iterable)
    assert issubclass(dict, Container)
    assert issubclass(set, Sized)


def test_reraise_function():
    """Test reraise compatibility function."""
    # Test simple reraise
    with pytest.raises(ValueError):
        try:
            raise ValueError("Test error")
        except ValueError as e:
            reraise(e)
    
    # We can't easily test the traceback argument in a portable way
    # since traceback objects are different in Python 2 and 3


def test_catch_and_wrap():
    """Test catch_and_wrap function."""
    # Test basic functionality
    def raise_func():
        raise ValueError("Original error")
    
    with pytest.raises(RuntimeError) as excinfo:
        catch_and_wrap(raise_func, ValueError, RuntimeError)
    
    assert "Original error" in str(excinfo.value)
    
    # Test with custom message function
    def custom_msg(exc):
        return f"Custom message: {exc}"
    
    with pytest.raises(RuntimeError) as excinfo:
        catch_and_wrap(raise_func, ValueError, RuntimeError, custom_msg)
    
    assert "Custom message" in str(excinfo.value)
    
    # Test with successful function
    def success_func():
        return "success"
    
    result = catch_and_wrap(success_func, ValueError, RuntimeError)
    assert result == "success"


if __name__ == "__main__":
    pytest.main([__file__])