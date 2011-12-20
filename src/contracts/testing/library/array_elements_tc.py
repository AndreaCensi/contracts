import numpy

from . import good, fail

arr01 = numpy.array([0, 1, 0, 1])
arr012 = numpy.array([0, 1, 0, 2])
arr124 = numpy.array([1, 2, 4])
arr125 = numpy.array([1, 2, 5])

good('array(=0|=1|=2)', arr01)
good('array(=0|=1|=2)', arr012)
good('array(=0|=1)', arr01)
fail('array(=0|=1)', arr012)

good('array(=4|>=0,<=2)', arr124)
good('array(=5|>=0,<=2)', arr125)
fail('array(=4|>=2,<=0)', arr124)

arr01int16 = numpy.zeros((3,), 'int16')
good('array(int16,(=0|=1))', arr01int16)
