from ..interface import (ContractSyntaxError, describe_value,
                         ContractNotRespected)
from ..main import parse_contract_string, check_contracts


def check_contracts_ok(contract, value):
    if isinstance(contract, str):
        contract = [contract]
        value = [value]
    context = check_contracts(contract, value)

    assert isinstance(context, dict)
    "%s" % context
    "%r" % context


def check_contracts_fail(contract, value, error=ContractNotRespected):
    """ Returns the exception """
    if isinstance(contract, str):
        contract = [contract]
        value = [value]

    try:
        context = check_contracts(contract, value)

        msg = ('I was expecting that the values would not not'
               ' satisfy the contract.\n')

        for v in value:
            msg += '      value: %s\n' % describe_value(v)

        for c in contract:
            cp = parse_contract_string(c)
            msg += '   contract: %r, parsed as %r (%s)\n' % (c, cp, cp)

        msg += '    context:  %r\n' % context

        raise Exception(msg)

    except error as e:
        # Try generation of strings:
        s = "%r" % e  # @UnusedVariable
        s = "%s" % e  # @UnusedVariable
        return e


def check_syntax_fail(string):
    assert isinstance(string, str)

    try:
        parsed_contract = parse_contract_string(string)
        msg = 'I would not expect to parse %r.' % string
        msg += ' contract:         %s\n' % parsed_contract
        raise Exception(msg)

    except ContractSyntaxError as e:
        # Try generation of strings:
        s = "%r" % e  # @UnusedVariable
        s = "%s" % e  # @UnusedVariable
        pass

