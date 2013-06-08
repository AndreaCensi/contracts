from numpy import zeros, ones
import numpy as np

from . import syntax_fail, good, fail
from contracts.library.array import np_int_dtypes, np_uint_dtypes, \
    np_float_dtypes

a_u8 = np.zeros((3, 4), dtype='uint8')
a_i8 = np.zeros((3, 4), dtype='int8')
a_u16 = np.zeros((3, 4), dtype='uint16')
a_i16 = np.zeros((3, 4), dtype='int16')
a_u32 = np.zeros((3, 4), dtype='uint32')
a_i32 = np.zeros((3, 4), dtype='int32')
a_f32 = np.zeros((3, 4), dtype='float32')
a_f64 = np.zeros((3, 4), dtype='float64')
a_bool = np.zeros((3, 4), dtype='bool')

# ## Strings
good('array', a_f32)
good('array', a_f64)
# synonims
good('ndarray', a_f32, exact=False)  # will be canonicalized to "array"
good('ndarray', a_f64, exact=False)  # same
fail('array', [0, 1])
# dtypes
good('array(uint8)', a_u8)
good('array(u1)', a_u8)
good('array(int8)', a_i8)
good('array(i1)', a_i8)
good('array(float32)', a_f32)
good('array(float64)', a_f64)
good('array(bool)', a_bool)
fail('array(float64)', a_f32)
fail('array(float32)', a_f64)
fail('array(uint8)', a_f32)
fail('array(float32)', a_u8)

# shapes
a0d = np.zeros((), dtype='float32')
a1d = np.zeros((2,))
a2d = np.zeros((2, 4,))
a3d = np.zeros((2, 4, 8))

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
good('array[(=2)x(>3)]', a2d, exact=False)  # Parenthesis are unnecessary

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

v1d = np.zeros(100)
v2d = np.zeros((10, 10))
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
A = np.array([0, 1, 2])
B = np.array([10, 20, 30])
good('array(>=0)', A)
good('array(<=2)', A)
fail('array(<=20)', B)
good('array(=0)', zeros((10)))
fail('array(=0)', np.array([0, 1, 0]))
good('array(=1)', ones((10)))

good(['shape(x)', 'shape(x)'], [a2d, a2d])
fail(['shape(x)', 'shape(x)'], [a2d, a3d])

good('array[NxN](<=1)', np.ones((10, 10)))
good('array[NxN](<=1,float32)', np.ones((10, 10), dtype='float32'))
good('array[NxN](<=1,float32|float64)', np.ones((10, 10), dtype='float64'))
good('array[NxN](<=1,(float32|float64))',
     np.ones((10, 10), dtype='float64'))
good('array[NxN](<=1,>=1)', np.ones((10, 10)))

# more complicated tests

good('array[(2|3)xN]', np.ones((2, 10)))
good('array[(2|3)xN]', np.ones((3, 10)))
fail('array[(2|3)xN]', np.ones((4, 10)))
good('array[(2|3)x...]', np.ones((2, 10)))
good('array[(2|3)x...]', np.ones((3, 10)))
fail('array[(2|3)x...]', np.ones((4, 10)))

good('array[(2,*)xN]', np.ones((2, 10)))
fail('array[(2,3)xN]', np.ones((4, 10)))
good('array[(2,*)x...]', np.ones((2, 10)))
fail('array[(2,3)x...]', np.ones((4, 10)))


good('seq', np.ones(3))
good('seq[3]', np.ones(3))
fail('seq[3]', np.ones(2))
good('seq[6]', np.ones((2, 3)))
fail('seq[6]', np.ones((2, 4)))

# "finite" contract 
good('finite', 1)
good('finite', 0)
good('finite', -1)
good('finite', np.float(1))
fail('finite', np.inf)
fail('finite', np.nan)


# generalized ideas of numbers
# np_ints = ['int8', 'int16', 'int32', 'int64',
#            'uint8', 'uint16', 'uint32', 'uint64',
#            ]
# np_floats = ['float32', 'float64']

good('array(float)', np.array(1.32, 'float32'))


for dt in np_int_dtypes:
    x = np.array(1).astype(dt)
    good('number', x)
    fail('Number', x)

    good('array(int)', x)
    good('int', x)
    fail('Int', x)

    fail('array(float)', x)
    fail('float', x)
    fail('Float', x)
    
# generalized ideas of numbers
for dt in np_float_dtypes:
    x = np.array(1).astype(dt)
    good('number', x)
    fail('Number', x)
    
    fail('array(int)', x)
    fail('int', x)
    fail('Int', x)

    good('array(float)', x)
    good('float', x)
    fail('Float', x)
    
# generalized ideas of numbers
for dt in np_uint_dtypes:
    x = np.array(1).astype(dt)
    good('number', x)
    fail('Number', x)
    
    fail('array(int)', x)
    fail('int', x)
    fail('Int', x)

    good('array(uint)', x)
    fail('Int', x)

    fail('array(float)', x)
    fail('float', x)
    fail('Float', x)

