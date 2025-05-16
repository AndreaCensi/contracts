from contracts.test_registrar import fail
from contracts.test_registrar import good

# dummy
good("*", 0)
good("*", [1])
good("*", None)

fail("#", None)

good("*|#", None)
fail("*,#", None)
