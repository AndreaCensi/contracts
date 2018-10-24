__version__ = '1.8.6'

import logging

# logging.basicConfig()
logger = logging.getLogger(__name__)

from .enabling import disable_all, enable_all, all_disabled
from .interface import (Contract, ContractNotRespected,
                        CannotDecorateClassmethods,
                        ContractSyntaxError, ContractException)
from .interface import describe_value, describe_type, describe_value_multiline
from .main import (check, fail, check_multiple, contract_decorator,
                   contracts_decorate as decorate,
                   parse_flexible_spec as parse)
from .main import new_contract as new_contract_main
from .metaclass import ContractsMeta, with_metaclass
from .useful_contracts import *
from .utils import *


# Just make them appear as belonging to the "contracts" Module
# So that Eclipse and other IDEs will not get confused.
def contract(*args, **kwargs):
    return contract_decorator(*args, **kwargs)


contract.__doc__ = contract_decorator.__doc__


def new_contract(*args):
    return new_contract_main(*args)


new_contract.__doc__ = new_contract_main.__doc__

# A couple of useful functions

ContractsMeta.__module__ = 'contracts'

# And after everything else is loaded, load the  utils
# After everything is loaded, load aliases
# from .library import miscellaneous_aliases  # @UnusedImport
