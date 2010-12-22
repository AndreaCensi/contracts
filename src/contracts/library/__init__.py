from .separate_context import SeparateContext
from . import separate_context_test

from .dummy import Any, Never
from . import dummy_test

from .types_misc import Type, CheckType, Number, NoneType
from . import types_test

from .strings import String
from . import strings_test

from .lists import List
from . import lists_test

from .tuple import Tuple
from . import tuple_test

from .dicts import Dict
from . import dicts_test

from .variables import BindVariable
from . import variables_test

from .simple_values import EqualTo
from . import simple_values_test

from .comparison import CheckOrder
from . import comparison_test

from .compositions import OR, And, composite_contract, or_contract
from . import compositions_test

from .arithmetic import Binary, Unary
from . import arithmetic_test

try: 
    import numpy
except ImportError: # pragma: no cover
    pass  
else:
    from .array import ShapeContract, Shape, Array, ArrayConstraint, DType, dtype
    from . import array_examples

