#!/usr/bin/env python
"""
Test script to verify PyContracts string handling compatibility between Python 2 and 3.
"""
import sys
import pytest

# Import from PyContracts
from contracts import contract, ContractNotRespected, new_contract
from contracts.interface import Where, printable_length_where
from contracts.py_compatibility import string_types, text_type, binary_type, PY3

def test_string_types():
    """Test the string_types compatibility layer."""
    # Simple string should be recognized as a string type
    assert isinstance("hello", string_types)
    
    # Unicode string should be recognized as a string type
    if not PY3:
        assert isinstance(u"hello", string_types)
    
    # Non-string should not be recognized as a string type
    assert not isinstance(123, string_types)
    assert not isinstance([1, 2, 3], string_types)

def test_where_class():
    """Test the Where class with different string types."""
    # Test with a simple string
    w = Where("hello world", 0, 5)
    assert w.get_substring() == "hello"
    
    # Test with a unicode string
    w = Where(u"hello world", 0, 5)
    assert w.get_substring() == u"hello"
    
    # Test with a long string
    long_str = "x" * 100
    w = Where(long_str, 50, 60)
    assert w.get_substring() == "x" * 10
    
    # Test error cases
    with pytest.raises(ValueError):
        Where(123, 0, 5)  # Not a string
    
    with pytest.raises(ValueError):
        Where("hello", 10, 5)  # Invalid indexes

def test_printable_length():
    """Test the printable_length_where function."""
    # Simple ASCII string
    w = Where("hello", 0, 5)
    assert printable_length_where(w) == 5
    
    # Unicode string
    w = Where(u"hello", 0, 5)
    assert printable_length_where(w) == 5
    
    # String with non-ASCII characters
    w = Where(u"héllo", 0, 5)
    assert printable_length_where(w) == 5

def test_string_contracts():
    """Test string contracts."""
    @contract(s='str')
    def process_string(s):
        return s.upper()
    
    # This should work
    assert process_string("hello") == "HELLO"
    
    # Unicode strings should work too
    assert process_string(u"hello") == u"HELLO"
    
    # These should fail
    with pytest.raises(ContractNotRespected):
        process_string(123)
    
    with pytest.raises(ContractNotRespected):
        process_string([1, 2, 3])

if __name__ == '__main__':
    print(f"Testing PyContracts string handling with Python {sys.version.split()[0]}")
    
    test_string_types()
    test_where_class()
    test_printable_length()
    test_string_contracts()
    
    print("All string compatibility tests passed successfully!")