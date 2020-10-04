import functools
try:
    # python 3.5+
    from functools import lru_cache
except ImportError:
    # python 2
    from backports.functools_lru_cache import lru_cache

try:
    # python 3.3+

    object.__qualname__

    import operator
    qualname = operator.attrgetter("__qualname__")
except AttributeError:
    # python 2
    from qualname import qualname

import attr  # attr is only a dependency of pycontracts if this module is imported. Otherwise, it does not depend on it.
from contracts.interface import ContractNotRespected
from contracts.main import new_contract


@attr.s(repr=False, slots=True, hash=True)
class AttrValidator(object):
    '''
        Validator linking C{pycontracts} with C{attr}'s validators
    '''

    def __call__(self, inst, attr, value):
        """
            Executes the validator by checking it against the contract it was configured with.
        """
        try:
            AttrValidator.__get_contract(inst.__class__, attr.name, self.contract).check(
                                   value,
                                   )
        except ContractNotRespected as e:
            # adding formatted debug information to the error
            e.error = "{!r}.{}\n{}".format(inst, attr.name, e.error)
            raise e

    def __repr__(self):
        return (
            "<Validator linking attr's validators with pycontracts' contract: {contract!r}>"
            .format(contract=self.contract)
        )

    @staticmethod
    @lru_cache(typed=True)
    def __get_contract(inst_class, name, contract):
        # compiling the contract takes time, we want to cache active contracts as they come up
        return new_contract("{}___{}".format(qualname(inst_class).replace('.', '___'), name), contract,)

    contract = attr.ib()
    """ Contract honoured by the given validator"""

