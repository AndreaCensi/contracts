#!/usr/bin/env python
"""
Test script to verify PyContracts compatibility with collections.abc.
"""
import sys
import traceback
import pytest

# Import from PyContracts
from contracts import contract, ContractNotRespected, new_contract
from contracts.py_compatibility import (
    Sequence, MutableSequence, 
    Mapping, MutableMapping,
    Set, MutableSet,
    Iterable, Container
)

def test_sequence_contract():
    """Test contracts with Sequence type."""
    @contract(s='seq')
    def process_sequence(s):
        return len(s)
    
    # These should work
    assert process_sequence([1, 2, 3]) == 3
    assert process_sequence((1, 2, 3)) == 3
    assert process_sequence("abc") == 3
    
    # This should fail
    with pytest.raises(ContractNotRespected):
        process_sequence({1, 2, 3})

def test_mapping_contract():
    """Test contracts with Mapping type."""
    @contract(m='map')
    def process_mapping(m):
        return len(m)
    
    # This should work
    assert process_mapping({'a': 1, 'b': 2}) == 2
    
    # These should fail
    with pytest.raises(ContractNotRespected):
        process_mapping([1, 2, 3])
    
    with pytest.raises(ContractNotRespected):
        process_mapping((1, 2, 3))

def test_set_contract():
    """Test contracts with Set type."""
    @contract(s='set')
    def process_set(s):
        return len(s)
    
    # This should work
    assert process_set({1, 2, 3}) == 3
    
    # These should fail
    with pytest.raises(ContractNotRespected):
        process_set([1, 2, 3])
    
    with pytest.raises(ContractNotRespected):
        process_set({'a': 1, 'b': 2})

def test_nested_contracts():
    """Test contracts with nested collection types."""
    @contract(data='map(str:seq)')
    def process_nested(data):
        return sum(len(v) for v in data.values())
    
    # This should work
    assert process_nested({'a': [1, 2], 'b': [3, 4, 5]}) == 5
    
    # These should fail
    with pytest.raises(ContractNotRespected):
        process_nested({'a': {1, 2}, 'b': [3, 4, 5]})
    
    with pytest.raises(ContractNotRespected):
        process_nested({1: [1, 2], 'b': [3, 4, 5]})

if __name__ == '__main__':
    print(f"Testing PyContracts collections.abc with Python {sys.version.split()[0]}")
    
    test_sequence_contract()
    test_mapping_contract()
    test_set_contract()
    test_nested_contracts()
    
    print("All collections tests passed successfully!")