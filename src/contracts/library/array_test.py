from contracts.test_registrar import syntax_fail, good, fail

import numpy

a = numpy.zeros((3, 4))

### Strings
good('array', a)
