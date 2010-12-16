from contracts.testing.utils import check_contracts_fail, check_contracts_ok

good_examples = []
fail_examples = []
def good_example(a, b): good_examples.append((a, b))
def fail_example(a, b): fail_examples.append((a, b))

# dummy
good_example(['*'], [0])
good_example(['*', '*'], [0, 1])
good_example(['=0', '=1'], [0, 1])
fail_example(['=0', '=1'], [0, 2])

# Lists of equal length
good_example(['list[N]', 'list[N]'], [ [4], [3]])
good_example(['list[N]', 'list[N]'], [ [], []])
fail_example(['list[N]', 'list[N]'], [ [], [1]])
good_example(['list[N]', 'list[N],N>0'], [ [1], [3]])
# we can also refer to the other context
good_example(['list[N]', 'list,N>0'], [ [1], [3]])
fail_example(['list[N]', 'list,N>0'], [ [], [3]])

# Lists of different length
good_example(['list[N]', 'list[M], M!=N'], [ [4], [3, 2]])
good_example(['list[N]', 'list[M], M!=N'], [ [4, 3 ], [3]])
fail_example(['list[N]', 'list[M], M!=N'], [ [3], [3]])

# One list shorter than the other
good_example(['list[N]', 'list[M], M<N'], [ [4, 3], [3]])
good_example(['list[N]', 'list[M], N>M'], [ [4, 3], [3]])
fail_example(['list[N]', 'list[M], N>M'], [ [3], [3]])

# Values of the same type
good_example(['type(x)', 'type(x)'], [0, 1])
good_example(['type(x)', 'type(x)'], [0.1, 1.1])
fail_example(['type(x)', 'type(x)'], [0.1, 1])
good_example(['type(x)', 'type(y)', 'type(x)|type(y)'], [0, 1.1, 1.2])
good_example(['type(x)', 'type(y)', 'type(x)|type(y)'], [0, 1.1, 3])
fail_example(['type(x)', 'type(y)', 'type(x)|type(y)'], [0, 1.1, 'ciao'])

# A list with all elements of the same type
good_example(['list(type(x))'], [ [0, 1, 2] ])
fail_example(['list(type(x))'], [ [0, 1.2, 2] ])
fail_example(['list(type(x))'], [ [0, None, 2] ])
# Lists with the same type of elements
good_example(['list(type(x))', 'list(type(x))'], [ [1, 2], [3, 4]])
fail_example(['list(type(x))', 'list(type(x))'], [ [1, 2], [3.0, 4]])
# Using different variables and then imposing they are equal
good_example(['list(type(x))', 'list(type(y)), x=y'], [ [1, 2], [3, 4]])
fail_example(['list(type(x))', 'list(type(y)), x=y'], [ [1, 2], [3.0, 4]])



def test_multiple_ok():
    for contracts, values in good_examples:
        assert len(contracts) == len(values)
        yield check_contracts_ok, contracts, values

def test_multiple_fail():
    for contracts, values in fail_examples:
        assert len(contracts) == len(values)
        yield check_contracts_fail, contracts, values

