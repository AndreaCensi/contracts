import io

from contracts.test_registrar import fail, good, syntax_fail

good("file", io.IOBase())
fail("file", 1)
fail("file", [])
syntax_fail("file[]")
syntax_fail("file[]()")
syntax_fail("file()")
