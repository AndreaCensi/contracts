from . import good, fail
import collections

# sequences
for obj in ([], tuple(), set(), frozenset(), collections.deque(), {}, 'ciao',):
    good('collection[*]', obj)
    good('collection[*]', obj)
    good('collection[*](*)', obj)
    good('collection[N]', obj)
    fail('collection[N],N>0', [])

for obj in ([1.], (1.,), {1.}, frozenset((1.,)), collections.deque((1.,)), {1.:1},):
    good('collection[*](float)', obj)
    good('collection[=1]', obj)
    fail('collection[=2]', obj)
    good('collection[1]', obj)  # shortcut

    good('collection[N],N>0', obj)
    good('collection[N],N=1', obj)
    good('collection[N],N>0,N<2', obj)

    fail('collection[*](int)', obj)

