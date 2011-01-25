from . import good, fail

# dummy
good('*', 0)
good('*', [1])
good('*', None)

fail('#', None)

good('*|#', None)
fail('*,#', None)
