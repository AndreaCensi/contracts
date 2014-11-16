from nose.tools import raises

from contracts import contract, parse, check, fail, decorate, ContractException


def test_raw_parse():
    p = 2
    c = parse('$p')
    assert c.rvalue.value == 2


def test_value_frozen_at_parsetime():
    p = 2
    c = parse('$p')
    p = 3
    assert c.rvalue.value == 2


def test_holds_reference():
    class Foo(object):
        pass

    assert parse('$Foo').rvalue.value is Foo


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
