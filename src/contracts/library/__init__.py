from . import separate_context
from . import separate_context_test

from . import dummy
from . import dummy_test

from . import types_misc
from . import types_test

from . import strings
from . import strings_test

from . import lists
from . import lists_test

from . import tuple
from . import tuple_test

from . import dicts
from . import dicts_test

from . import variables
from . import variables_test

from . import simple_values
from . import simple_values_test

from . import comparison
from . import comparison_test

from . import compositions
from . import compositions_test

from . import arithmetic
from . import arithmetic_test

try: 
    import numpy
    use_numpy = True
except:
    use_numpy = False

if use_numpy:
    from . import array_examples
    from . import array
    
