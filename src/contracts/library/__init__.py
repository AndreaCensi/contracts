from . import dummy
from . import dummy_test

from . import types
from . import types_test

from . import strings
from . import strings_test

from . import lists
from . import lists_test

from . import tuple
from . import tuple_test

from . import variables
from . import variables_test

from . import simple_values
from . import simple_values_test

from . import comparison
from . import comparison_test

from . import compositions
from . import compositions_test

try: 
    import numpy
    from . import array
    from . import array_test
except:
    pass
