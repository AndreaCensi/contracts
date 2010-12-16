from contracts.test_registrar import syntax_fail, good, fail

import numpy

a = numpy.zeros((3, 4))

### Strings
good('array', a)


rgb1 = numpy.zeros((10, 10, 3), 'uint8')
rgb2 = numpy.zeros((20, 20, 3), 'uint8')
# will fail if you don't rewrite
# alias  rgb = rewrite( array[HxWx3](uint8) )
#good(['rgb', 'rgb'], [rgb1, rgb2]) 
