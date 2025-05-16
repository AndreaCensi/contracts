__version__ = "7.3"

import logging

# logging.basicConfig()
logger = logging.getLogger(__name__)

from .interface import CannotDecorateClassmethods
from .interface import Contract
from .interface import ContractException
from .interface import ContractNotRespected
from .interface import ContractSyntaxError
from .main import check
from .main import check_multiple
from .main import contract_decorator
from .main import contracts_decorate as decorate
from .main import fail
from .main import parse_flexible_spec as parse


# Just make them appear as belonging to the "contracts" Module
# So that Eclipse and other IDEs will not get confused.
def contract(*args, **kwargs):
    return contract_decorator(*args, **kwargs)


contract.__doc__ = contract_decorator.__doc__

from .main import new_contract as new_contract_main


def new_contract(*args):
    return new_contract_main(*args)


new_contract.__doc__ = new_contract_main.__doc__

from .enabling import all_disabled
from .enabling import disable_all
from .enabling import enable_all
from .interface import describe_type

# A couple of useful functions
from .interface import describe_value
from .interface import describe_value_multiline
from .metaclass import ContractsMeta
from .metaclass import with_metaclass
from .utils import *

ContractsMeta.__module__ = "contracts"

# And after everything else is loaded, load the  utils
from .useful_contracts import *

# After everything is loaded, load aliases
# from .library import miscellaneous_aliases  # @UnusedImport
