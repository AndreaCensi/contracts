#cython: language_level=3, annotation_typing=True, c_string_encoding=utf-8, boundscheck=False, wraparound=False, initializedcheck=False
import numpy as np
from Aspidites._vendor.contracts import new_contract
from Aspidites._vendor.contracts.interface import describe_value, describe_type
__all__ = ['finite']


@new_contract
def finite(x):
    return np.isfinite(x).all()


new_contract('np_scalar_uint', 'np_uint8|np_uint16|np_uint32|np_uint64')
new_contract('np_scalar_int', 'np_int8|np_int16|np_int32|np_int64')
new_contract('np_scalar_float', 'np_float32|np_float64')
new_contract('np_scalar_type', 'np_scalar_int|np_scalar_uint|np_scalar_float')


@new_contract
def np_zeroshape_array(x):
    scalars: tuple = (
    np.ndarray,
    np.int,  # Platform integer (normally either int32 or int64)
    np.int8,  # Byte (-128 to 127)
    np.int16,  # Integer (-32768 to 32767)
    np.int32,  # Integer (-2147483648 to 2147483647)
    np.int64,  # Integer (-9223372036854775808 to 9223372036854775807)
    np.uint8,  # Unsigned integer (0 to 255)
    np.uint16,  # Unsigned integer (0 to 65535)
    np.uint32,  # Unsigned integer (0 to 4294967295)
    np.uint64,  # Unsigned integer (0 to 18446744073709551615)
    np.float,  # Shorthand for float64.
    np.float16,  #  Half precision float: sign bit, 5 bits exponent, 10 bits mantissa
    np.float32,  #  Single precision float: sign bit, 8 bits exponent, 23 bits mantissa
    np.float64,  #  Double precision float: sign bit, 11 bits exponent, 52 bits mantissa
    np.complex,  #  Shorthand for complex128.
    np.complex64,  #    Complex number, represented by two 32-bit floats (real and imaginary components)
    np.complex128
    )

    if not isinstance(x, np.ndarray):
        msg = 'Not an array: %s %s ' % (type(x), describe_type(x))
        raise ValueError(msg)

    if not x.shape == ():
        msg = 'Not a scalar: %s' % describe_value(x)
        raise ValueError(msg)

    return True


new_contract('np_scalar', 'np_zeroshape_array|np_scalar_type')

