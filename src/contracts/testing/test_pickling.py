from .utils import check_contracts_fail
from contracts import ContractNotRespected, parse, Contract
from contracts.test_registrar import (semantic_fail_examples,
    contract_fail_examples, good_examples)
import pickle


def check_exception_pickable(contract, value):
    exception = check_contracts_fail(contract, value)
    assert isinstance(exception, Exception)
    try:
        s = pickle.dumps(exception)
        pickle.loads(s)
    except TypeError as e:
        print('While pickling: %s' % exception)
        raise e
        # msg = 'Could not pickle exception.\n'
        # msg += str(exception)
        # msg += 'Raised: %s' % e
        # raise Exception(msg)


import pytest

@pytest.mark.parametrize('contract,value,exact', semantic_fail_examples + contract_fail_examples)
def test_exceptions_are_pickable(contract, value, exact):  # @UnusedVariable
    check_contracts_fail(contract, value, ContractNotRespected)


def check_contract_pickable(contract):
    c = parse(contract)
    assert isinstance(c, Contract)
    try:
        s = pickle.dumps(c)
        c2 = pickle.loads(s)
    except TypeError as e:
        msg = 'Could not pickle contract.\n'
        msg += '- string: %s\n' % c
        msg += '-   repr: %r\n' % c
        msg += 'Exception: %s' % e
        raise Exception(msg)

    assert c == c2


def get_all_contracts():
    """Helper function to extract all contracts for parameterization"""
    all_contracts = []
    allc = (good_examples + semantic_fail_examples + contract_fail_examples)
    for contract, _, _ in allc:
        if isinstance(contract, list):
            all_contracts.extend(contract)
        else:
            all_contracts.append(contract)
    return all_contracts

@pytest.mark.parametrize('contract', get_all_contracts())
def test_contracts_are_pickable(contract):
    check_contract_pickable(contract)
