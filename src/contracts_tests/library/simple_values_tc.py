import math

from contracts.test_registrar import fail, good

good("0", 0)
good("1", 1)
fail("1", 2)

good("pi", math.pi)
fail("pi", math.pi * 2)
