from . import good, fail
import math


good('0', 0)
good('1', 1)
fail('1', 2)

good('pi', math.pi)
fail('pi', math.pi * 2)
