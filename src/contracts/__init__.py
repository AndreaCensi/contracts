
__version__ = '0.9.2'

from . import syntax 
contract_expression = syntax.contract

from .interface import (Contract, Context, ContractNotRespected,
                        ContractSyntaxError, ContractException)

from .main import (check, fail, check_multiple, contracts, new_contract)
from .main import parse_flexible_spec as parse
from .main import contracts_decorate as decorate


# After everything is loaded, load aliases
from .library import miscellaneous_aliases 
