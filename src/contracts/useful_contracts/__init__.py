try:
    import numpy
except ImportError:  # pragma: no cover
    pass
else:
    from .numpy_specific import *    

from .numbers import *
