""" Other testing examples """

from ..test_registrar import good, fail

# dummy
good(['*'], [0])
good(['*', '*'], [0, 1])
good(['=0', '=1'], [0, 1])
fail(['=0', '=1'], [0, 2])

# Lists of equal length
good(['list[N]', 'list[N]'], [[4], [3]])
good(['list[N]', 'list[N]'], [[], []])
fail(['list[N]', 'list[N]'], [[], [1]])
good(['list[N]', 'list[N],N>0'], [[1], [3]])
# we can also refer to the other context
good(['list[N]', 'list,N>0'], [[1], [3]])
fail(['list[N]', 'list,N>0'], [[], [3]])

# Lists of different length
good(['list[N]', 'list[M],M!=N'], [[4], [3, 2]])
good(['list[N]', 'list[M],M!=N'], [[4, 3], [3]])
fail(['list[N]', 'list[M],M!=N'], [[3], [3]])

# One list shorter than the other
good(['list[N]', 'list[M],M<N'], [[4, 3], [3]])
good(['list[N]', 'list[M],N>M'], [[4, 3], [3]])
fail(['list[N]', 'list[M],N>M'], [[3], [3]])

# Values of the same type
good(['type(x)', 'type(x)'], [0, 1])
good(['type(x)', 'type(x)'], [0.1, 1.1])
fail(['type(x)', 'type(x)'], [0.1, 1])
good(['type(x)', 'type(y)', 'type(x)|type(y)'], [0, 1.1, 1.2])
good(['type(x)', 'type(y)', 'type(x)|type(y)'], [0, 1.1, 3])
fail(['type(x)', 'type(y)', 'type(x)|type(y)'], [0, 1.1, 'ciao'])

# A list with all elements of the same type
good(['list(type(x))'], [[0, 1, 2]])
fail(['list(type(x))'], [[0, 1.2, 2]])
fail(['list(type(x))'], [[0, None, 2]])
# Lists with the same type of elements
good(['list(type(x))', 'list(type(x))'], [[1, 2], [3, 4]])
fail(['list(type(x))', 'list(type(x))'], [[1, 2], [3.0, 4]])
# Using different variables and then imposing they are equal
good(['list(type(x))', 'list(type(y)),x=y'], [[1, 2], [3, 4]])
fail(['list(type(x))', 'list(type(y)),x=y'], [[1, 2], [3.0, 4]])

# a list with at most two types
good('list(type(x|y))', [1, 2, 3, 4.0])
fail('list(type(x|y))', [1, 2, 'ciao', 4.0])


