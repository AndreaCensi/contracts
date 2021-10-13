#cython: language_level=3, annotation_typing=True, c_string_encoding=utf-8, boundscheck=False, wraparound=False, initializedcheck=False
from Aspidites._vendor.contracts.main import new_contract
from math import isfinite

try:
    import numpy  # @UnusedImport
except ImportError:  # pragma: no cover
    __all__ = ['finite']
    new_contract('float', 'Float')
    new_contract('int', 'Int')
    new_contract('number', 'float|int')

    @new_contract
    def finite(x):
        return isfinite(x)
else:
    __all__ = []
    new_contract('float', 'Float|np_scalar_float|(np_scalar, array(float))')
    new_contract('int', 'Int|np_scalar_int|(np_scalar,array(int))')
    new_contract('uint', 'np_scalar_uint|(np_scalar, array(uint))')
    new_contract('number', 'float|int|uint')



