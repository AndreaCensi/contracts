
__version__ = '0.9'

from .interface import (Contract, Context, ContractNotRespected,
                        ContractSyntaxError, ContractException)

from .main import (check, check_multiple, contracts, new_contract)

from .main import parse_contract_string as parse
from .main import contracts_decorate as decorate
from . import syntax 

contract_expression = syntax.contract
