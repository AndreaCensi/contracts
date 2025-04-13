#!/usr/bin/env python
"""
Test script to verify PyContracts inspection.py functionality.
"""
import pytest
from contracts.inspection import (
    can_be_used_as_a_type, can_accept_exactly_one_argument,
    get_callable_fullargspec, can_accept_at_least_one_argument,
    can_accept_self, can_accept_self_plus_one_argument,
    check_callable_accepts_these_arguments, InvalidArgs
)


class OldStyleClass:
    """Old style class for testing."""
    pass


class TypeClass(type):
    """Type class for testing."""
    pass


class TestClass:
    """Test class for various function tests."""
    def method_no_args(self):
        pass
    
    def method_one_arg(self, arg):
        pass
    
    def method_varargs(self, *args):
        pass
    
    def method_kwargs(self, **kwargs):
        pass
    
    def method_complex(self, arg1, arg2, *args, **kwargs):
        pass


def function_no_args():
    pass


def function_one_arg(arg):
    pass


def function_varargs(*args):
    pass


def function_kwargs(**kwargs):
    pass


def function_complex(arg1, arg2, *args, **kwargs):
    pass


def test_can_be_used_as_a_type():
    """Test can_be_used_as_a_type function."""
    # Standard types should work
    assert can_be_used_as_a_type(int)
    assert can_be_used_as_a_type(str)
    assert can_be_used_as_a_type(list)
    assert can_be_used_as_a_type(dict)
    assert can_be_used_as_a_type(object)
    
    # Custom classes should work
    assert can_be_used_as_a_type(TestClass)
    
    # Type classes should work
    assert can_be_used_as_a_type(TypeClass)
    
    # Non-types should not work
    assert not can_be_used_as_a_type(1)
    assert not can_be_used_as_a_type("test")
    assert not can_be_used_as_a_type([])
    assert not can_be_used_as_a_type({})


def test_can_accept_exactly_one_argument():
    """Test can_accept_exactly_one_argument function."""
    # Functions that accept exactly one argument
    result, msg = can_accept_exactly_one_argument(function_one_arg)
    assert result
    
    # Functions that accept no arguments
    result, msg = can_accept_exactly_one_argument(function_no_args)
    assert not result
    
    # Functions that accept variable arguments
    result, msg = can_accept_exactly_one_argument(function_varargs)
    assert result  # This should work because it can accept one arg
    
    # Methods that accept exactly one argument (plus self)
    test_instance = TestClass()
    result, msg = can_accept_exactly_one_argument(test_instance.method_one_arg)
    assert result
    
    # Methods that accept no additional arguments
    result, msg = can_accept_exactly_one_argument(test_instance.method_no_args)
    assert not result


def test_get_callable_fullargspec():
    """Test get_callable_fullargspec function."""
    # Function
    spec = get_callable_fullargspec(function_one_arg)
    assert spec.args == ['arg']
    
    # Method
    test_instance = TestClass()
    spec = get_callable_fullargspec(test_instance.method_one_arg)
    assert spec.args == ['self', 'arg']
    
    # Complex function
    spec = get_callable_fullargspec(function_complex)
    assert spec.args == ['arg1', 'arg2']
    assert spec.varargs == 'args'
    assert spec.varkw == 'kwargs'


def test_can_accept_at_least_one_argument():
    """Test can_accept_at_least_one_argument function."""
    # Functions that accept at least one argument
    assert can_accept_at_least_one_argument(function_one_arg)
    assert can_accept_at_least_one_argument(function_complex)
    
    # Functions that accept variable arguments
    assert can_accept_at_least_one_argument(function_varargs)
    
    # Functions that accept no arguments
    assert not can_accept_at_least_one_argument(function_no_args)
    
    # Functions that accept only keyword arguments
    assert not can_accept_at_least_one_argument(function_kwargs)


def test_can_accept_self():
    """Test can_accept_self function."""
    # Methods should have self
    test_instance = TestClass()
    assert can_accept_self(test_instance.method_no_args)
    assert can_accept_self(test_instance.method_one_arg)
    
    # Functions should not have self
    assert not can_accept_self(function_no_args)
    assert not can_accept_self(function_one_arg)


def test_can_accept_self_plus_one_argument():
    """Test can_accept_self_plus_one_argument function."""
    # Methods that accept self plus one argument
    test_instance = TestClass()
    assert can_accept_self_plus_one_argument(test_instance.method_one_arg)
    
    # Methods that only accept self
    assert not can_accept_self_plus_one_argument(test_instance.method_no_args)
    
    # Functions don't have self
    assert not can_accept_self_plus_one_argument(function_one_arg)
    assert not can_accept_self_plus_one_argument(function_no_args)


def test_check_callable_accepts_these_arguments():
    """Test check_callable_accepts_these_arguments function."""
    # Valid calls
    assert check_callable_accepts_these_arguments(function_one_arg, ('test',), {})
    assert check_callable_accepts_these_arguments(function_complex, ('arg1', 'arg2'), {})
    assert check_callable_accepts_these_arguments(function_complex, ('arg1',), {'arg2': 'value'})
    assert check_callable_accepts_these_arguments(function_varargs, ('a', 'b', 'c'), {})
    assert check_callable_accepts_these_arguments(function_kwargs, (), {'a': 1, 'b': 2})
    
    # Invalid calls
    with pytest.raises(InvalidArgs):
        check_callable_accepts_these_arguments(function_no_args, ('too_many',), {})
    
    with pytest.raises(InvalidArgs):
        check_callable_accepts_these_arguments(function_one_arg, (), {})  # Missing required arg
    
    with pytest.raises(InvalidArgs):
        check_callable_accepts_these_arguments(function_one_arg, ('a', 'b'), {})  # Too many args


if __name__ == "__main__":
    pytest.main([__file__])