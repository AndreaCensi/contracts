__version__ = '1.6.4'

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)

from . import syntax
contract_expression = syntax.contract_expression

from .interface import (Contract, ContractNotRespected, CannotDecorateClassmethods,
                        ContractSyntaxError, ContractException)

from .main import (check, fail, check_multiple, contract_decorator,
                    contracts_decorate as decorate,
                    parse_flexible_spec as parse)

# Just make them appear as belonging to the "contracts" Module
# So that Eclipse and other IDEs will not get confused.
def contract(*args, **kwargs):
    return contract_decorator(*args, **kwargs)
contract.__doc__ = contract_decorator.__doc__

from .main import new_contract as new_contract_main
def new_contract(*args, **kwargs):
    return new_contract_main(*args, **kwargs)
new_contract.__doc__ = new_contract_main.__doc__

from .enabling import disable_all, enable_all, all_disabled

# A couple of useful functions
from .interface import describe_value, describe_type
from .utils import *

# For backwards compatibility
# contracts = contract

# After everything is loaded, load aliases
from .library import miscellaneous_aliases

from .metaclass import ContractsMeta
ContractsMeta.__module__ = 'contracts'

# And after everything else is loaded, load the  utils
from .useful_contracts import *
