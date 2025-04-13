#!/usr/bin/env python
"""
Test specifically for Python 3.12 compatibility with collections.abc.
"""
import sys
import pytest

# Import from PyContracts
from contracts import contract, ContractNotRespected, new_contract
import contracts.py_compatibility as compat

# Only run these tests on Python 3.12+
requires_py312 = pytest.mark.skipif(
    not compat.PY3_12_PLUS,
    reason="These tests specifically target Python 3.12+ compatibility"
)

@requires_py312
def test_collections_abc_imports():
    """Test that collections.abc imports work in Python 3.12+."""
    # These should all be imported from collections.abc in Python 3.12+
    assert compat.Sequence.__module__ == 'collections.abc'
    assert compat.Mapping.__module__ == 'collections.abc'
    assert compat.Set.__module__ == 'collections.abc'
    assert compat.Iterable.__module__ == 'collections.abc'
    assert compat.Container.__module__ == 'collections.abc'
    assert compat.Sized.__module__ == 'collections.abc'

@requires_py312
def test_map_contract_py312():
    """Test map contract in Python 3.12+."""
    @contract(data='map')
    def process_map(data):
        return {k: v * 2 for k, v in data.items()}
    
    result = process_map({'a': 1, 'b': 2})
    assert result == {'a': 2, 'b': 4}

@requires_py312
def test_seq_contract_py312():
    """Test seq contract in Python 3.12+."""
    @contract(items='seq')
    def process_seq(items):
        return [x * 2 for x in items]
    
    result = process_seq([1, 2, 3])
    assert result == [2, 4, 6]

@requires_py312
def test_set_contract_py312():
    """Test set contract in Python 3.12+."""
    @contract(items='set')
    def process_set(items):
        return {x * 2 for x in items}
    
    result = process_set({1, 2, 3})
    assert result == {2, 4, 6}

@requires_py312
def test_nested_collections_py312():
    """Test nested collections in Python 3.12+."""
    @contract(data='map(str:seq)')
    def process_nested(data):
        return {k: [x * 2 for x in v] for k, v in data.items()}
    
    result = process_nested({'a': [1, 2], 'b': [3, 4]})
    assert result == {'a': [2, 4], 'b': [6, 8]}

if __name__ == '__main__':
    if compat.PY3_12_PLUS:
        print(f"Testing PyContracts with Python {sys.version.split()[0]} (3.12+)")
        
        test_collections_abc_imports()
        test_map_contract_py312()
        test_seq_contract_py312()
        test_set_contract_py312()
        test_nested_collections_py312()
        
        print("All Python 3.12+ compatibility tests passed successfully!")
    else:
        print(f"Skipping Python 3.12+ specific tests (running on Python {sys.version.split()[0]})")