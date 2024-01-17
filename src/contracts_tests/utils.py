from typing import List, Type, Union

from contracts.interface import ContractNotRespected, ContractSyntaxError, describe_value
from contracts.main import check_contracts, parse_contract_string


def check_contracts_ok(contract: Union[str, List[str]], value: object):
    if isinstance(contract, str):
        contract = [contract]
        value = [value]
    context = check_contracts(contract, value)

    assert isinstance(context, dict)
    _ = "%s" % context
    _ = "%r" % context


def check_contracts_fail(contract: Union[str, List[str]], value: object, error: Type[Exception] = ContractNotRespected):
    """Returns the exception"""
    if isinstance(contract, str):
        contract = [contract]
        value = [value]

    try:
        context = check_contracts(contract, value)

        msg = "I was expecting that the values would not not" " satisfy the contract.\n"

        for v in value:
            msg += "      value: %s\n" % describe_value(v)

        for c in contract:
            cp = parse_contract_string(c)
            msg += "   contract: %r, parsed as %r (%s)\n" % (c, cp, cp)

        msg += "    context:  %r\n" % context

        raise Exception(msg)

    except error as e:
        # Try generation of strings:
        s = "%r" % e  # @UnusedVariable
        s = "%s" % e  # @UnusedVariable
        return e


def check_syntax_fail(string: str):
    assert isinstance(string, str)

    try:
        parsed_contract = parse_contract_string(string)
        msg = "I would not expect to parse %r." % string
        msg += " contract:         %s\n" % parsed_contract
        raise Exception(msg)

    except ContractSyntaxError as e:
        # Try generation of strings:
        s = "%r" % e  # @UnusedVariable
        s = "%s" % e  # @UnusedVariable
        pass
