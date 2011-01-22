from ...test_registrar import syntax_fail, good, fail, semantic_fail

from . import dummy_test
from . import separate_context_test
from . import types_test
from . import strings_test
from . import lists_test
from . import tuple_test
from . import dicts_test
from . import comparison_test
from . import arithmetic_test
from . import compositions_test
from . import variables_test
from . import simple_values_test

try: 
    import numpy
except ImportError: # pragma: no cover
    pass  
else:
    from . import array_tests
    
