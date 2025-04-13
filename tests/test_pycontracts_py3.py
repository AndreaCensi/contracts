#!/usr/bin/env python
"""
Test script to verify PyContracts compatibility with Python 3.
"""
import sys
import traceback

# Import from our patched PyContracts
sys.path.insert(0, './vendor')
from contracts import contract, ContractNotRespected, new_contract

def test_basic_contracts():
    """Test basic contract functionality."""
    print("Testing basic contracts...")
    
    @contract(a='int,>0', b='list[N](int),N>0')
    def my_function(a, b):
        return a * sum(b)
    
    # This should work
    try:
        result = my_function(5, [1, 2, 3])
        print(f"  Success: my_function(5, [1, 2, 3]) = {result}")
    except Exception as e:
        print(f"  FAILED: {e}")
        traceback.print_exc()
    
    # This should fail with a contract violation
    try:
        my_function(-5, [1, 2, 3])
        print("  FAILED: Expected contract violation but call succeeded")
    except ContractNotRespected as e:
        print("  Success: Contract violation correctly detected")
    except Exception as e:
        print(f"  FAILED: Wrong exception type: {type(e).__name__}")
        traceback.print_exc()

def test_collection_contracts():
    """Test contracts with collection types that moved to collections.abc in Python 3.12."""
    print("\nTesting collection type contracts...")
    
    @contract(s='set', m='map')
    def test_collections(s, m):
        return len(s) + len(m)
    
    # This should work
    try:
        result = test_collections({1, 2, 3}, {'a': 1, 'b': 2})
        print(f"  Success: test_collections({1, 2, 3}, {{'a': 1, 'b': 2}}) = {result}")
    except Exception as e:
        print(f"  FAILED: {e}")
        traceback.print_exc()
    
    # This should fail
    try:
        test_collections([1, 2, 3], {'a': 1, 'b': 2})
        print("  FAILED: Expected contract violation but call succeeded")
    except ContractNotRespected as e:
        print("  Success: Contract violation correctly detected")
    except Exception as e:
        print(f"  FAILED: Wrong exception type: {type(e).__name__}")
        traceback.print_exc()

def test_custom_contracts():
    """Test custom contract definitions."""
    print("\nTesting custom contracts...")
    
    # Define a custom contract
    new_contract('positive_list', 'list[N](int,>0),N>0')
    
    @contract(x='positive_list')
    def sum_positive(x):
        return sum(x)
    
    # This should work
    try:
        result = sum_positive([1, 2, 3])
        print(f"  Success: sum_positive([1, 2, 3]) = {result}")
    except Exception as e:
        print(f"  FAILED: {e}")
        traceback.print_exc()
    
    # This should fail
    try:
        sum_positive([1, -2, 3])
        print("  FAILED: Expected contract violation but call succeeded")
    except ContractNotRespected as e:
        print("  Success: Contract violation correctly detected")
    except Exception as e:
        print(f"  FAILED: Wrong exception type: {type(e).__name__}")
        traceback.print_exc()

def test_exception_handling():
    """Test the exception handling in contracts."""
    print("\nTesting exception handling...")
    
    # Define a contract that will cause a validation error
    @contract(x='int,>0')
    def positive_reciprocal(x):
        return 1/x
    
    # This should work fine
    try:
        result = positive_reciprocal(5)
        print(f"  Success: positive_reciprocal(5) = {result}")
    except Exception as e:
        print(f"  FAILED: {e}")
        traceback.print_exc()
    
    # This should fail with contract violation
    try:
        positive_reciprocal(-5)
        print("  FAILED: Expected contract violation but call succeeded")
    except ContractNotRespected:
        print("  Success: Contract violation correctly detected")
    except Exception as e:
        print(f"  FAILED: Wrong exception type: {type(e).__name__}")
        traceback.print_exc()
    
    # This should fail with ZeroDivisionError but wrapped
    try:
        positive_reciprocal(0)
        print("  FAILED: Expected ZeroDivisionError but call succeeded")
    except ContractNotRespected:
        print("  Success: ZeroDivisionError properly wrapped in ContractNotRespected")
    except ZeroDivisionError:
        print("  FAILED: Raw ZeroDivisionError not wrapped")
    except Exception as e:
        print(f"  FAILED: Wrong exception type: {type(e).__name__}")
        traceback.print_exc()

if __name__ == '__main__':
    print(f"Testing PyContracts with Python {sys.version.split()[0]}")
    
    test_basic_contracts()
    test_collection_contracts()
    test_custom_contracts()
    test_exception_handling()
    
    print("\nAll tests completed.")