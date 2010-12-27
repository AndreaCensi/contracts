
__version__ = '0.9.1'

from . import syntax 

from . import syntax 

from .interface import (Contract, Context, ContractNotRespected,
                        ContractSyntaxError, ContractException)

from .main import (check, fail, check_multiple, contracts, new_contract)

from .main import parse_flexible_spec as parse
from .main import contracts_decorate as decorate

contract_expression = syntax.contract


# After everything is loaded, load aliases
from .library import miscellaneous_aliases 


# Some old experiments to allow use of the whole module as a decorator. 
#
#  import contracts
#
#  @contracts
#  def f():
#     ...
#  
# import types
# class mod_call(types.ModuleType):
# 
#     def __init__(self):
#         types.ModuleType.__init__(self, 'contracts')
# 
#     __call__ = contracts
# #    def __call__(*arg, **args):
#  #       return contracts(*arg,**args)
#     # __name__ = 'contracts'
#     
#     from .interface import (Contract, Context, ContractNotRespected,
#                             ContractSyntaxError, ContractException)
# 
#     from .main import (check, check_multiple, contracts, new_contract)
# 
#     from .main import parse_contract_string as parse
#     from .main import contracts_decorate as decorate
#     from . import syntax 
# 
#     contract_expression = syntax.contract
# 
#     # After everything is loaded, load aliases
#     from .library import miscellaneous_aliases 
# 
#     from . import testing
#     
# import sys
# avatar = mod_call()
# print(avatar)
# sys.modules[__name__] = avatar

