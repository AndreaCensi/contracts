from contracts.main import new_contract

__all__ = []

try:
    import numpy  # @UnusedImport
except ImportError:  # pragma: no cover
    new_contract('float', 'Float')
    new_contract('int', 'Int')
    new_contract('number', 'float|int')    
else:
    new_contract('float', 'Float|np_scalar_float|(np_scalar, array(float))')
    new_contract('int', 'Int|np_scalar_int|(np_scalar,array(int))')
    new_contract('uint', 'np_scalar_uint|(np_scalar, array(uint))')
    new_contract('number', 'float|int|uint')

    
    
