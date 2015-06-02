import io
import sys

from ..interface import Contract, ContractNotRespected
from ..syntax import (add_contract, add_keyword, Keyword, W)

if sys.version_info[0] > 2:
    file_type = io.IOBase
else:
    file_type = (file, io.IOBase)

class File(Contract):

    def check_contract(self, context, value):
        if not isinstance(value, file_type):
            error = 'Expected a file, got %r.' % value.__class__.__name__
            raise ContractNotRespected(contract=self, error=error,
                                       value=value, context=context)

    def __str__(self):
        return 'file'

    def __repr__(self):
        return 'File()'

    @staticmethod
    def parse_action(s, loc, _):
        where = W(s, loc)
        return File(where=where)


file_contract = Keyword('file')

file_contract.setParseAction(File.parse_action)

add_contract(file_contract)
add_keyword('file')
