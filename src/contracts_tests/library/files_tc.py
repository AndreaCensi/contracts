import io

from contracts.test_registrar import fail
from contracts.test_registrar import good
from contracts.test_registrar import syntax_fail

good("file", io.IOBase())
fail("file", 1)
fail("file", [])
syntax_fail("file[]")
syntax_fail("file[]()")
syntax_fail("file()")
