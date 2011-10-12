__version__ = '1.2.0'

from . import syntax 
contract_expression = syntax.contract_expression

from .interface import (Contract, ContractNotRespected,
                        ContractSyntaxError, ContractException)

from .main import (check, fail, check_multiple, contract_decorator as contract,
                    new_contract,
                    contracts_decorate as decorate,
                    parse_flexible_spec as parse)

from .enabling import disable_all, enable_all, all_disabled

# A couple of useful functions
from .interface import describe_value, describe_type

# For backwards compatibility
contracts = contract   

# After everything is loaded, load aliases
from .library import miscellaneous_aliases 

