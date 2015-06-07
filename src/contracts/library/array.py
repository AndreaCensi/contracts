from ..interface import Contract, ContractNotRespected, describe_type
from ..pyparsing_utils import myOperatorPrecedence
from ..syntax import (add_contract, W, contract_expression, O, S, rvalue,
    simple_contract, ZeroOrMore, Literal, MatchFirst, opAssoc, FollowedBy, NotAny,
    Keyword, add_keyword, Word)
from .array_ops import (ArrayOR, ArrayAnd, DType, ArrayConstraint,
    ArrayORCustomString)
from .compositions import And, OR
from .suggester import create_suggester
from numpy import ndarray, dtype  # @UnusedImport
import numpy
from pyparsing import operatorPrecedence


class Array(Contract):

    def __init__(self, shape_contract=None,
                        elements_contract=None, where=None):
        Contract.__init__(self, where)
        self.shape_contract = shape_contract
        self.elements_contract = elements_contract

    def check_contract(self, context, value, silent):
        if not isinstance(value, ndarray):
            error = 'Expected an array, got a %s.' % describe_type(value)
            raise ContractNotRespected(contract=self, error=error,
                                       value=value, context=context)

        if self.shape_contract is not None:
            self.shape_contract._check_contract(context, value.shape, silent)

        if self.elements_contract is not None:
            self.elements_contract._check_contract(context, value, silent)

    def __str__(self):
        s = 'array'
        if self.shape_contract is not None:
            s += '[%s]' % self.shape_contract
        if self.elements_contract is not None:
            s += '(%s)' % self.elements_contract
        return s

    def __repr__(self):
        s = 'Array(%r,%r)' % (self.shape_contract, self.elements_contract)
        return s

    @staticmethod
    def parse_action(s, loc, tokens):
        where = W(s, loc)
        shape_contract = tokens.get('shape_contract', [None])[0]
        elements_contract = tokens.get('elements_contract', [None])[0]

        assert shape_contract is None or isinstance(shape_contract,
                                                    ShapeContract)
        assert elements_contract is None or isinstance(elements_contract,
                                                       Contract)
        return Array(shape_contract, elements_contract, where=where)


class ShapeContract(Contract):
    def __init__(self, dimensions, ellipsis=False, where=None):
        assert isinstance(dimensions, list)
        assert isinstance(ellipsis, bool)
        Contract.__init__(self, where)
        self.dimensions = dimensions
        self.ellipsis = ellipsis

    def check_contract(self, context, value, silent):
        assert isinstance(value, tuple)  # Guaranteed by construction

        expected = len(self.dimensions)
        ndim = len(value)

        if ndim < expected:  # TODO: write clearer message
            error = 'Expected %d dimensions, got %d.' % (expected, ndim)
            raise ContractNotRespected(contract=self, error=error,
                                       value=value, context=context)

        if ndim > expected and not self.ellipsis:
            error = 'Expected %d dimensions, got %d.' % (expected, ndim)
            raise ContractNotRespected(contract=self, error=error,
                                       value=value, context=context)

        for i in range(expected):
            self.dimensions[i]._check_contract(context, value[i], silent)

    def __str__(self):
        be_careful = self.ellipsis or len(self.dimensions) > 1

        def rep(x):
            if be_careful and isinstance(x, (And, OR)):
                return "(%s)" % x
            else:
                return "%s" % x

        s = 'x'.join(rep(x) for x in self.dimensions)
        if self.ellipsis:
            s += 'x...'
        return s

    def __repr__(self):
        if self.ellipsis:
            s = 'ShapeContract(%r,%r)' % (self.dimensions, self.ellipsis)
        else:
            s = 'ShapeContract(%r)' % self.dimensions
        return s

    @staticmethod
    def parse_action(s, loc, tokens):
        where = W(s, loc)
        # print "in tokens: " % tokens
        # workaround for some bugs
        ellipsis = False
        dimensions = []
        for t in tokens:
            if t == '...':
                ellipsis = True
            else:
                assert isinstance(t, Contract), 'Wrong token %r' % t
                dimensions.append(t)
        return ShapeContract(dimensions, ellipsis, where=where)


class Shape(Contract):
    def __init__(self, length, contract, where=None):
        Contract.__init__(self, where)
        self.contract = contract
        self.length = length

    def check_contract(self, context, value, silent):
        if not isinstance(value, ndarray):
            error = 'Expected an array, got %r.' % value.__class__.__name__
            raise ContractNotRespected(contract=self, error=error,
                                       value=value, context=context)

        if isinstance(value, ndarray):
            value = value.shape

        if self.length is not None:
            self.length._check_contract(context, len(value), silent)

        if self.contract is not None:
            self.contract._check_contract(context, value, silent)

    def __str__(self):
        s = 'shape'
        if self.length is not None:
            s += '[%s]' % self.length
        if self.contract is not None:
            s += '(%s)' % self.contract
        return s

    def __repr__(self):
        s = 'Shape(%r,%r)' % (self.length, self.contract)
        return s

    @staticmethod
    def parse_action(s, loc, tokens):
        where = W(s, loc)
        assert 0 <= len(tokens) <= 2
        length = tokens.get('length', [None])[0]
        contract = tokens.get('other', [None])[0]
        return Shape(length, contract, where)


array_constraints = []
for glyph in ArrayConstraint.constraints:
    if glyph == '!=':
        # special case: ! must be followed by =
        glyph_expression = Literal('!') - Literal('=')
        glyph_expression.setName('!=')
    else:
        glyph_expression = Literal(glyph)

    expr = glyph_expression('glyph') - rvalue('rvalue')
    expr.setParseAction(ArrayConstraint.parse_action)
    array_constraints.append(expr)

np_uint_dtypes = "u1 uint8 uint16 uint32 uint64".split()
np_int_dtypes = "i1 int8 int16 int32 int64".split()
np_float_dtypes = "float32 float64".split()
np_other_dtypes = ['bool']  
atomic = np_uint_dtypes + np_int_dtypes + np_float_dtypes + np_other_dtypes

# in numpy, int = int64, float = float64
# for us, int = int64|int32| ...

dtype_checks = []
for x in atomic:
    d = numpy.dtype(x)
    expr = Keyword(x).setParseAction(DType.parse_action(d))
    dtype_checks.append(expr)
    
def np_composite(custom_string, alternatives):
    alts = [DType(numpy.dtype(a), a) for a in alternatives] 
    return ArrayORCustomString(custom_string=custom_string, clauses=alts)
    
def np_uint(s, loc, tokens):  # @UnusedVariable
    return np_composite('uint', np_uint_dtypes)
 
def np_int(s, loc, tokens):  # @UnusedVariable
    return np_composite('int', np_int_dtypes)

def np_float(s, loc, tokens):  # @UnusedVariable
    return np_composite('float', np_float_dtypes)

dtype_checks.append(Keyword('int').setParseAction(np_int))
dtype_checks.append(Keyword('uint').setParseAction(np_uint))
dtype_checks.append(Keyword('float').setParseAction(np_float))

composite = ['int', 'uint', 'float']

ndarray_simple_contract = MatchFirst(dtype_checks + array_constraints)
ndarray_simple_contract.setName('numpy element contract')

suggester = create_suggester(get_options=lambda: atomic + composite)
baseExpr = ndarray_simple_contract | suggester
baseExpr.setName('numpy contract (with recovery)')

op = myOperatorPrecedence
# op = operatorPrecedence
ndarray_composite_contract = op(baseExpr, [
    (',', 2, opAssoc.LEFT, ArrayAnd.parse_action),  # @UndefinedVariable
    ('|', 2, opAssoc.LEFT, ArrayOR.parse_action),  # @UndefinedVariable
])


def my_delim_list2(what, delim):
    return (what + ZeroOrMore(S(delim) + FollowedBy(NotAny(ellipsis)) - what))


ellipsis = Literal('...')

shape_suggester = create_suggester(get_options=lambda: ['...'],
                                   pattern=Word('.'))

inside_inside1 = simple_contract | shape_suggester
inside_inside2 = contract_expression | shape_suggester
inside = (S('(') - inside_inside2 - S(')')) | inside_inside1  # XXX: ^ and use or_contract?
shape_contract = my_delim_list2(inside, S('x')) + O(S('x') + ellipsis)
shape_contract.setParseAction(ShapeContract.parse_action)
shape_contract.setName('array shape contract')

name = Keyword('array') | Keyword('ndarray')
optional_shape = (S('[') - shape_contract - S(']'))('shape_contract')
optional_elements = (S('(') - ndarray_composite_contract - S(')'))('elements_contract')
array_contract = name + O(optional_shape) + O(optional_elements)
array_contract.setParseAction(Array.parse_action)
array_contract.setName('array() contract')
add_contract(array_contract)
add_keyword('array')
add_keyword('ndarray')

optional_length = (S('[') - contract_expression - S(']'))('length')
optional_other = (S('(') - contract_expression - S(')'))('other')
shape = Keyword('shape') + O(optional_length) + O(optional_other)
shape.setName('shape() contract')
shape.setParseAction(Shape.parse_action)
add_contract(shape)
add_keyword('shape')




