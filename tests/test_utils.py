#!/usr/bin/env python
"""
Test script to verify PyContracts utils.py functions.
"""
import pytest
from contracts.utils import (
    indent, deprecated, raise_type_mismatch, raise_wrapped,
    raise_desc, check_isinstance, format_dict_long,
    format_list_long, format_obs, ignore_typeerror
)
from contracts.py_compatibility import string_types, PY3


def test_indent():
    """Test the indent function."""
    # Test with string
    result = indent("line1\nline2", "+ ")
    assert result == "+ line1\n+ line2"
    
    # Test with first prefix
    result = indent("line1\nline2", "+ ", first="* ")
    assert result == "* line1\n+ line2"
    
    # Test with non-string (should be converted)
    result = indent(123, "+ ")
    assert result == "+ 123"


def test_deprecated():
    """Test the deprecated decorator."""
    @deprecated
    def old_function():
        return "result"
    
    # Verify function still works
    with pytest.warns(DeprecationWarning):
        result = old_function()
    
    assert result == "result"
    
    # Verify metadata is preserved
    assert old_function.__name__ == "old_function"


def test_check_isinstance():
    """Test check_isinstance function."""
    # Should not raise when type matches
    check_isinstance("test", string_types)
    
    # Should raise when type doesn't match
    with pytest.raises(ValueError):
        check_isinstance(123, string_types)


def test_raise_type_mismatch():
    """Test raise_type_mismatch function."""
    with pytest.raises(ValueError) as excinfo:
        raise_type_mismatch(123, string_types, context="test_context")
    
    # Verify error message contains expected information
    error_msg = str(excinfo.value)
    assert "expected: " in error_msg
    assert "obtained: " in error_msg
    assert "context: " in error_msg


def test_format_obs():
    """Test format_obs function."""
    result = format_obs({"name": "test", "value": 123})
    
    # Verify result contains the keys and values
    assert "name" in result
    assert "test" in result
    assert "value" in result
    assert "123" in result


def test_format_dict_long():
    """Test format_dict_long function."""
    result = format_dict_long({"key1": "value1", "key2": 123})
    
    # Verify result contains the keys and values
    assert "key1" in result
    assert "value1" in result
    assert "key2" in result
    assert "123" in result


def test_format_list_long():
    """Test format_list_long function."""
    result = format_list_long(["item1", 123])
    
    # Verify result contains the items with markers
    assert "- item1" in result
    # The format is "- Instance of <class 'int'>.\n  123"
    assert "- Instance of" in result
    assert "123" in result


def test_raise_desc():
    """Test raise_desc function."""
    with pytest.raises(ValueError) as excinfo:
        raise_desc(ValueError, "Error message", param="test")
    
    # Verify error message contains description and parameters
    error_msg = str(excinfo.value)
    assert "Error message" in error_msg
    assert "param" in error_msg
    assert "test" in error_msg
    
    # Test args_first parameter
    with pytest.raises(ValueError) as excinfo:
        raise_desc(ValueError, "Error message", args_first=True, param="test")
    
    error_msg = str(excinfo.value)
    # The args should come before the message
    param_pos = error_msg.find("param")
    msg_pos = error_msg.find("Error message")
    assert param_pos < msg_pos


def test_raise_wrapped():
    """Test raise_wrapped function."""
    try:
        # Generate an exception to wrap
        raise ValueError("Original error")
    except ValueError as e:
        with pytest.raises(RuntimeError) as excinfo:
            raise_wrapped(RuntimeError, e, "Wrapped error", param="test")
        
        # Verify error message contains original error and new context
        error_msg = str(excinfo.value)
        assert "Wrapped error" in error_msg
        assert "Original error" in error_msg
        assert "param" in error_msg
        assert "test" in error_msg


def test_ignore_typeerror():
    """Test ignore_typeerror decorator."""
    @ignore_typeerror
    def function_with_typeerror():
        raise TypeError("Type error")
    
    # Should convert TypeError to Exception
    with pytest.raises(Exception) as excinfo:
        function_with_typeerror()
    
    assert "TypeError" in str(excinfo.value)


if __name__ == "__main__":
    pytest.main([__file__])
