from contracts import ContractException, check, contract, decorate, fail, parse
from contracts.interface import (ContractNotRespected,
    ExternalScopedVariableNotFound)
from contracts.library.simple_values import EqualTo
from contracts.library.types_misc import CheckType
from contracts.utils import check_isinstance
from nose.tools import raises


def test_raw_parse():
    p = 2
    c = parse('$p')
    assert c.rvalue.value == 2


def test_value_frozen_at_parsetime():
    p = 2
    c = parse('$p')
    p = 3

    check_isinstance(c, EqualTo)
    assert c.rvalue.value == 2

    c = parse('$p')
    check_isinstance(c, EqualTo)
    assert c.rvalue.value == 3

def test_holds_reference():
    class Foo(object):
        pass
    c = parse('$Foo')
    check_isinstance(c, CheckType)
    
    assert c.types == Foo


def test_algebra():

    p = 2
    c = parse('list[$p]')

    assert c.length_contract.rvalue.value == 2


@raises(ContractException)
def test_invalid():
    parse('$not_found')


def test_check():
    p = 2
    q = 4
    c = parse('list[$p](>$q)')

    c.check([5, 10])
    c.fail([5, 3])


def test_contract_decorator():
    z = 1

    @contract(x='$z')
    def foo(x):
        pass

    foo(1)


def test_contract_decorate():
    z = 1

    def foo(x):
        pass

    c = decorate(foo, x='$z')
    c(1)


def test_check_fail():
    z = 2
    check('$z', 2)
    fail('$z', 3)


def test_contract_not_cached():
    z = 2
    check('$z', 2)
    z = 3
    check('$z', 3)


def test_self_referential():
    try:
        class MyClass():
            def __init__(self):
                pass
            @contract(other='$MyClass')
            def compare(self, other):
                pass
    except ExternalScopedVariableNotFound as e:
        assert e.get_token() == 'MyClass'
    else:
        raise ValueError()



def test_class_ref():
    class MyClass():
        def __init__(self, a):
            self.a = a
              
    @contract(x='$MyClass')  
    def f1(x):
        pass
    
    f1(MyClass(1))  # OK

    try:
        f1(1)  # raise
    except ContractNotRespected as e:
        pass
    else:
        raise ValueError()

