from Aspidites._vendor.contracts import new_contract

try:
    import numpy
except ImportError:  # pragma: no cover
    pass
else:
    from .numpy_specific import *    

from .numbers import *


new_contract('bytes', bytes)
