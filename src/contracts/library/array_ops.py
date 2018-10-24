from abc import abstractmethod

import numpy as np

from .types_misc import CheckType
from ..interface import Contract, ContractNotRespected, RValue, eval_in_context
from ..syntax import W, Keyword, add_contract, add_keyword


class ArrayElementsTest(Contract):

    @abstractmethod
    def test_elements(self, context, value):
        """ Returns either a bool or an array of bool. """

    def check_contract(self, context, value, silent):
        result = self.test_elements(context, value)

        if np.all(result):
            return

        result = np.array(result)  # for simple bool
        resultf = result.flatten()
        valuef = value.flatten()
        some, = np.nonzero(np.logical_not(resultf))
        num = value.size
        num_fail = len(some)
        perc = 100.0 * num_fail / num
        error = ("In this array, %d/%d (%f%%) of elements do not respect "
                 "the condition %s." % (num_fail, num, perc, self))
        some_failures = valuef[some]
        MAX_N = 4
        if len(some_failures) > MAX_N:
            some_failures = some_failures[:MAX_N]
        failures = list(some_failures)
        N = len(failures)
        error += '\nThese are the first %d: %s.' % (N, failures)
        raise ContractNotRespected(self, error, value, context)


class ArrayLogical(ArrayElementsTest):
    def __init__(self, glyph, precedence):
        self.glyph = glyph
        self.precedence = precedence

    def __str__(self):
        def convert(x):
            if isinstance(x, ArrayLogical) and x.precedence < self.precedence:
                return '(%s)' % x
            else:
                return '%s' % x

        s = self.glyph.join(convert(x) for x in self.clauses)
        return s


class ArrayOR(ArrayLogical):
    def __init__(self, clauses, where=None):
        assert isinstance(clauses, list)
        assert len(clauses) >= 2
        for c in clauses:
            assert isinstance(c, ArrayElementsTest)
        Contract.__init__(self, where)
        ArrayLogical.__init__(self, '|', 1)
        self.clauses = clauses

    def test_elements(self, context, value):
        assert isinstance(value, np.ndarray)
        result = False
        for c in self.clauses:
            result_c = c.test_elements(context, value)
            result = np.logical_or(result_c, result)
        return result

    def __repr__(self):
        s = 'ArrayOR(%r)' % self.clauses
        return s

    @staticmethod
    def parse_action(string, location, tokens):
        l = list(tokens[0])
        clauses = [l.pop(0)]
        while l:
            glyph = l.pop(0)  # @UnusedVariable
            assert glyph == '|'
            operand = l.pop(0)
            clauses.append(operand)
        where = W(string, location)
        return ArrayOR(clauses, where=where)


class ArrayORCustomString(ArrayOR):
    def __init__(self, custom_string, **other):
        self.custom_string = custom_string
        ArrayOR.__init__(self, **other)

    def __str__(self):
        return self.custom_string


class ArrayAnd(ArrayLogical):
    def __init__(self, clauses, where=None):
        assert isinstance(clauses, list)
        assert len(clauses) >= 2, clauses
        assert isinstance(clauses, list)
        assert len(clauses) >= 2
        for c in clauses:
            assert isinstance(c, ArrayElementsTest)

        Contract.__init__(self, where)
        ArrayLogical.__init__(self, ',', 2)
        self.clauses = clauses

    def test_elements(self, context, value):
        assert isinstance(value, np.ndarray)
        result = True
        for c in self.clauses:
            result_c = c.test_elements(context, value)
            result = np.logical_and(result_c, result)
        return result

    def __repr__(self):
        s = 'ArrayAnd(%r)' % self.clauses
        return s

    @staticmethod
    def parse_action(string, location, tokens):
        l = list(tokens[0])
        clauses = [l.pop(0)]
        while l:
            glyph = l.pop(0)  # @UnusedVariable
            assert glyph == ','
            operand = l.pop(0)
            clauses.append(operand)
        where = W(string, location)
        return ArrayAnd(clauses, where=where)


class ArrayConstraint(ArrayElementsTest):
    """ Comparisons for numpy array elements. They check that
        the condition is respected for all the entries in the array. """

    constraints = {
        '=': lambda x, rvalue: x == rvalue,
        '==': lambda x, rvalue: x == rvalue,
        '!=': lambda x, rvalue: x != rvalue,
        '>': lambda x, rvalue: x > rvalue,
        '>=': lambda x, rvalue: x >= rvalue,
        '<': lambda x, rvalue: x < rvalue,
        '<=': lambda x, rvalue: x <= rvalue,
    }

    def __init__(self, glyph, rvalue, where=None):
        assert glyph in ArrayConstraint.constraints
        assert isinstance(rvalue, RValue)
        Contract.__init__(self, where)
        self.glyph = glyph
        self.rvalue = rvalue

    def test_elements(self, context, value):
        """ Returns either a bool or an array of bool. """
        assert isinstance(value, np.ndarray)
        bound = eval_in_context(context=context, value=self.rvalue,
                                contract=self)

        operation = ArrayConstraint.constraints[self.glyph]
        result = operation(value, bound)
        return result

    def __str__(self):
        return '%s%s' % (self.glyph, self.rvalue)

    def __repr__(self):
        return 'ArrayConstraint(%r,%r)' % (self.glyph, self.rvalue)

    @staticmethod
    def parse_action(s, loc, tokens):
        where = W(s, loc)
        glyph = "".join(tokens['glyph'])
        rvalue = tokens['rvalue']
        return ArrayConstraint(glyph, rvalue, where)


class DType(ArrayElementsTest):
    """ Checks that the value is an array with the given dtype. """

    def __init__(self, dtype, dtype_string=None, where=None):
        assert isinstance(dtype, np.dtype)
        Contract.__init__(self, where)
        self.dtype = dtype
        if dtype_string is None:
            dtype_string = "%s" % dtype
        self.dtype_string = dtype_string

    def test_elements(self, context, value):  # @UnusedVariable
        assert isinstance(value, np.ndarray)  # Guaranteed by construction
        return value.dtype == self.dtype

    def __str__(self):
        return self.dtype_string

    def __repr__(self):
        if "%s" % self.dtype == self.dtype_string:
            return 'DType(%r)' % self.dtype
        else:
            return 'DType(%r,%r)' % (self.dtype, self.dtype_string)

    @staticmethod
    def parse_action(dtype=None):
        assert dtype is None or isinstance(dtype, np.dtype)

        def parse(s, loc, tokens):
            where = W(s, loc)
            dtype_string = tokens[0]
            if dtype is None:
                use_dtype = np.dtype(dtype_string)
            else:
                use_dtype = dtype
            return DType(use_dtype, dtype_string, where)

        return parse


np_types = {
    'np_int': np.int,  # Platform integer (normally either int32 or int64)
    'np_int8': np.int8,  # Byte (-128 to 127)
    'np_int16': np.int16,  # Integer (-32768 to 32767)
    'np_int32': np.int32,  # Integer (-2147483648 to 2147483647)
    'np_int64': np.int64,  # Integer (9223372036854775808 to 9223372036854775807)
    'np_uint8': np.uint8,  # Unsigned integer (0 to 255)
    'np_uint16': np.uint16,  # Unsigned integer (0 to 65535)
    'np_uint32': np.uint32,  # Unsigned integer (0 to 4294967295)
    'np_uint64': np.uint64,  # Unsigned integer (0 to 18446744073709551615)
    'np_float': np.float,  # Shorthand for float64.
    'np_float16': np.float16,  # Half precision float: sign bit, 5 bits exponent, 10 bits mantissa
    'np_float32': np.float32,  # Single precision float: sign bit, 8 bits exponent, 23 bits mantissa
    'np_float64': np.float64,  # Double precision float: sign bit, 11 bits exponent, 52 bits mantissa
    'np_complex': np.complex,  # Shorthand for complex128.
    'np_complex64': np.complex64,  # Complex number, represented by two 32-bit floats (real and imaginary components)
    'np_complex128': np.complex128}

for k, t in np_types.items():
    add_contract(Keyword(k).setParseAction(CheckType.parse_action(t)))
    add_keyword(k)
