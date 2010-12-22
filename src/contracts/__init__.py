
__version__ = '0.9'

from .interface import (Contract, Context, ContractNotRespected,
                        ContractSyntaxError, ContractException)

from .main import (check, check_multiple, check_contracts)
                   

from .main import parse_contract_string as parse
from .syntax import contract as contract_expression
