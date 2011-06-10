__version__ = '0.9.4'

from . import syntax 
contract_expression = syntax.contract_expression

from .interface import (Contract, Context, ContractNotRespected,
                        ContractSyntaxError, ContractException)

from .main import (check, fail, check_multiple, contract, new_contract)
from .main import parse_flexible_spec as parse
from .main import contracts_decorate as decorate

from .enabling import disable_all, enable_all, all_disabled

# For backwards compatibility
contracts = contract   

# After everything is loaded, load aliases
from .library import miscellaneous_aliases 

