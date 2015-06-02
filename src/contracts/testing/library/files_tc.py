import io

from . import syntax_fail, good, fail

good('file', io.IOBase())
fail('file', 1)
fail('file', [])
syntax_fail('file[]')
syntax_fail('file[]()')
syntax_fail('file()')
