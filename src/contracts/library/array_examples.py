from numpy import zeros, ones
import numpy

from ..test_registrar import syntax_fail, good, fail

a_u8 = numpy.zeros((3, 4), dtype='uint8')
a_i8 = numpy.zeros((3, 4), dtype='int8')
a_u16 = numpy.zeros((3, 4), dtype='uint16')
a_i16 = numpy.zeros((3, 4), dtype='int16')
a_u32 = numpy.zeros((3, 4), dtype='uint32')
a_i32 = numpy.zeros((3, 4), dtype='int32')
a_f32 = numpy.zeros((3, 4), dtype='float32')
a_f64 = numpy.zeros((3, 4), dtype='float64')

### Strings
good('array', a_f32)
good('array', a_f64)
# synonims
good('ndarray', a_f32, exact=False) # will be canonicalized to "array"
good('ndarray', a_f64, exact=False) # same
fail('array', [0, 1])
# dtypes
good('array(uint8)', a_u8)
good('array(u1)', a_u8)
good('array(int8)', a_i8)
good('array(i1)', a_i8)
good('array(float32)', a_f32)
good('array(float64)', a_f64)
fail('array(float64)', a_f32)
fail('array(float32)', a_f64)
fail('array(uint8)', a_f32)
fail('array(float32)', a_u8)

# shapes
a0d = numpy.zeros((), dtype='float32')
a1d = numpy.zeros((2,))
a2d = numpy.zeros((2, 4,))
a3d = numpy.zeros((2, 4, 8))

good('shape[0]', a0d)
good('shape[1]', a1d)
good('shape[2]', a2d)
good('shape[3]', a3d)
fail('shape[>0]', a0d)
fail('shape[<1]', a1d)
fail('shape[>2]', a2d)
fail('shape[<3]', a3d)
good(['shape[x]', 'shape[y],x=y'], [a3d, a3d])
good(['shape[x]', 'shape[y],x=y'], [a2d, a2d])
good(['shape[x]', 'shape[y],x=y'], [a1d, a1d])
good(['shape[x]', 'shape[y],x=y'], [a0d, a0d])

good('array[2x4]', a2d)
fail('array[AxBxC]', a2d)
fail('array[2x4]', a3d)

good('array[HxW],H=2,W>3', a2d)
good('array[(=2)x(>3)]', a2d, exact=False) # Parenthesis are unnecessary

# ellipsis to mean 0 or more dimensions 
good('array[2x4x...]', a2d)
good('array[2x4x...]', a3d)

# if we really want more, use:
good('shape[>2],array[2x4x...]', a3d)
fail('shape[>2],array[2x4x...]', a2d)

fail('shape[>2]', [2, 2, 3])

# Try some binding:
good('array[XxYx...],X=2,Y=4', a3d)

# We don't do in between yet
syntax_fail('array[2x...x3]')

# We don't do in between yet
syntax_fail('array[2x...x3]')
# Try some binding:
good('array[XxYx...],X=2,Y=4', a2d)
good('array[XxYx...],X=2,Y=4', a3d)

# Using the array syntax  array[shape desc]

v1d = numpy.zeros(100)
v2d = numpy.zeros((10, 10))
good('array[100]', v1d)
fail('array[100]', v2d)
good('array[10x10]', v2d)
fail('array[10x...]', v1d)
good('array[10x...]', v2d)

fail('shape[>0]', a0d)
fail('shape[<1]', a1d)
fail('shape[>2]', a2d)
fail('shape[<3]', a3d)
good('shape[0]', a0d)
good('shape[1]', a1d)
good('shape[2]', a2d)
good('shape[3]', a3d)
# TODO: check this
# good('array[shape[3]]', a3d)

good('array[1x2]', zeros((1, 2)))

# Now: special comparisons for arrays
A = numpy.array([0, 1, 2])
B = numpy.array([10, 20, 30])
good('array(>=0)', A)
good('array(<=2)', A)
fail('array(<=20)', B)
good('array(=0)', zeros((10)))
fail('array(=0)', numpy.array([0, 1, 0]))
good('array(=1)', ones((10)))

good(['shape(x)', 'shape(x)'], [a2d, a2d])
fail(['shape(x)', 'shape(x)'], [a2d, a3d])

## Shortcuts for images
#rgb1 = numpy.zeros((10, 10, 3), 'uint8')
#rgb2 = numpy.zeros((20, 20, 3), 'uint8')
#rgba1 = numpy.zeros((10, 10, 4), 'uint8')
#good(['rgb', 'rgb'], [rgb1, rgb2]) 
#fail('rgba', rgb1)
#fail('rgb', rgba1)
#good('rgb|rgba', rgb1) 
#good('rgb|rgba', rgba1)

# TODO
# can be converted to an array
#good('as_array', [0, 1])
#fail('as_array', None)

# TODO: finite, notnan, etc.
