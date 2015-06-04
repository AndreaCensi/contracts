from ...test_registrar import syntax_fail, good, fail, semantic_fail

from . import dummy_tc
from . import separate_context_tc
from . import types_tc
from . import strings_tc
from . import lists_tc
from . import tuple_tc
from . import dicts_tc
from . import comparison_tc
from . import arithmetic_tc
from . import compositions_tc
from . import variables_tc
from . import simple_values_tc
from . import map_tc
from . import seq_tc
from . import attr_tc
from . import files_tc

from . import isinstance_tc 

from . import extensions_tc

try:
    import numpy
except ImportError:  # pragma: no cover
    pass
else:
    from . import array_tc
    from . import array_elements_tc

