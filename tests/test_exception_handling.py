#!/usr/bin/env python
"""
Test script to verify PyContracts exception handling compatibility between Python 2 and 3.
"""
import sys
import pytest

# Import from PyContracts
from contracts import contract, ContractNotRespected, new_contract
from contracts.interface import Contract
from contracts.py_compatibility import reraise, catch_and_wrap, PY3

def test_basic_exception_handling():
    """Test basic contract exception handling."""
    @contract(x='int,>0')
    def positive_reciprocal(x):
        return 1/x
    
    # This should work
    assert positive_reciprocal(5) == 0.2
    
    # This should fail with contract violation
    with pytest.raises(ContractNotRespected):
        positive_reciprocal(-5)
    
    # This should fail with ZeroDivisionError wrapped in ContractNotRespected
    with pytest.raises(ContractNotRespected):
        positive_reciprocal(0)

def test_custom_contract_exceptions():
    """Test that custom contract validation errors are properly wrapped."""
    # Define custom contract validator function that raises ValueError
    def value_error_validator(x):
        raise ValueError("Custom validation error")
    
    # Register the contract validator
    new_contract('value_error_contract', value_error_validator)

    # Test with ValueError - should be wrapped in ContractNotRespected
    @contract(x='value_error_contract')
    def test_value_error(x):
        return x
    
    with pytest.raises(ContractNotRespected):
        test_value_error(42)

def test_reraise_function():
    """Test the reraise compatibility function."""
    try:
        # Raise an exception
        raise ValueError("Original error")
    except ValueError as e:
        try:
            # Reraise it
            reraise(e)
            assert False, "reraise() didn't raise the exception"
        except ValueError:
            # This is expected
            pass

def test_catch_and_wrap_function():
    """Test the catch_and_wrap compatibility function."""
    # Define a function that will raise an exception
    def raise_value_error():
        raise ValueError("Original error")
    
    # Define a wrapper exception
    class WrapperException(Exception):
        pass
    
    # Test catching and wrapping the exception
    with pytest.raises(WrapperException):
        catch_and_wrap(raise_value_error, ValueError, WrapperException)
    
    # Test with a custom message function
    def message_func(e):
        return f"Wrapped error: {e}"
    
    try:
        catch_and_wrap(raise_value_error, ValueError, WrapperException, message_func)
        assert False, "catch_and_wrap() didn't raise the exception"
    except WrapperException as e:
        assert str(e).startswith("Wrapped error: ")

if __name__ == '__main__':
    print(f"Testing PyContracts exception handling with Python {sys.version.split()[0]}")
    
    test_basic_exception_handling()
    test_custom_contract_exceptions()
    test_reraise_function()
    test_catch_and_wrap_function()
    
    print("All exception handling tests passed successfully!")