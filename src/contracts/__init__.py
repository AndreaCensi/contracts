
__version__ = '0.9'

from .interface import (Contract, Context, ContractNotRespected,
                        ContractSyntaxError, ContractException)

from .main import (check, check_multiple, check_contracts, contracts,
                   contracts_decorate, new_contract)

from .main import parse_contract_string as parse

from . import syntax 

contract_expression = syntax.contract
