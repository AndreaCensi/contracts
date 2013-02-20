import numpy as np
from contracts.main import new_contract


@new_contract
def finite(x):
    return np.isfinite(x).all()

@new_contract
def scalar_number(x):
    """ Anything that acts like a number. """
    # TODO
