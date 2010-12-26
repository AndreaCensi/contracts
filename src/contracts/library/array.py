import numpy
from numpy  import ndarray, dtype #@UnusedImport

from ..interface import Contract, ContractNotRespected, RValue
from ..syntax import (add_contract, W, contract, O, S, rvalue,
                       simple_contract, ZeroOrMore, Literal, MatchFirst,
                        opAssoc, FollowedBy, NotAny, Keyword,
                       add_keyword, Word)
from ..pyparsing_utils import myOperatorPrecedence 

from .compositions import And, OR
from .suggester import create_suggester


class Array(Contract):
    
    def __init__(self, shape_contract=None, elements_contract=None, where=None):
        Contract.__init__(self, where)
        self.shape_contract = shape_contract
        self.elements_contract = elements_contract
    
    def check_contract(self, context, value): 
        if not isinstance(value, ndarray):
            error = 'Expected an array, got %r.' % value.__class__.__name__
            raise ContractNotRespected(contract=self, error=error,
                                       value=value, context=context)
       
        if self.shape_contract is not None:
            self.shape_contract._check_contract(context, value.shape)
        
        if self.elements_contract is not None:
            self.elements_contract._check_contract(context, value)
    
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
        
        assert shape_contract is None or isinstance(shape_contract, ShapeContract)
        assert elements_contract is None or isinstance(elements_contract, Contract)
        return Array(shape_contract, elements_contract, where=where)


class ShapeContract(Contract):
    def __init__(self, dimensions, ellipsis=False, where=None):
        assert isinstance(dimensions, list)
        assert isinstance(ellipsis, bool)
        Contract.__init__(self, where)
        self.dimensions = dimensions
        self.ellipsis = ellipsis
    
    def check_contract(self, context, value):
        assert isinstance(value, tuple) # Guaranteed by construction

        expected = len(self.dimensions)
        ndim = len(value)
    
        if ndim < expected: # TODO: write clearer message
            error = 'Expected %d dimensions, got %d.' % (expected, ndim)
            raise ContractNotRespected(contract=self, error=error,
                                       value=value, context=context)
        
        if ndim > expected and not self.ellipsis:
            error = 'Expected %d dimensions, got %d.' % (expected, ndim) 
            raise ContractNotRespected(contract=self, error=error,
                                       value=value, context=context)
        
        for i in range(expected):
            self.dimensions[i]._check_contract(context, value[i])
        
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
        #print "in tokens: " % tokens
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
    
    def check_contract(self, context, value):
        if not isinstance(value, ndarray):
            error = 'Expected an array, got %r.' % value.__class__.__name__
            raise ContractNotRespected(contract=self, error=error,
                                       value=value, context=context)       
        
        if isinstance(value, ndarray):
            value = value.shape
            
        if self.length is not None:
            self.length._check_contract(context, len(value))
            
        if self.contract is not None:
            self.contract._check_contract(context, value)
    
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
    
    
class DType(Contract):
    ''' Checks that the value is an array with the given dtype. ''' 
    def __init__(self, dtype, dtype_string=None, where=None):
        assert isinstance(dtype, numpy.dtype)
        Contract.__init__(self, where)
        self.dtype = dtype
        if dtype_string is None:
            dtype_string = "%s" % dtype
        self.dtype_string = dtype_string
    
    def check_contract(self, context, value):
        assert isinstance(value, ndarray) # Guaranteed by construction
        
        if not (value.dtype == self.dtype):
            error = ('Expected array with dtype %r, got %r.' % 
                     (self.dtype, value.dtype)) 
            raise ContractNotRespected(self, error, value, context)
     
    def __str__(self):
        return self.dtype_string
    
    def __repr__(self):
        if  "%s" % self.dtype == self.dtype_string:
            return 'DType(%r)' % self.dtype
        else:
            return 'DType(%r,%r)' % (self.dtype, self.dtype_string)
        
        
    @staticmethod 
    def parse_action(dtype=None):
        assert dtype is None or isinstance(dtype, numpy.dtype)
        def parse(s, loc, tokens):
            where = W(s, loc)
            dtype_string = tokens[0]
            if dtype is None:
                use_dtype = numpy.dtype(dtype_string)
            else:
                use_dtype = dtype
            return DType(use_dtype, dtype_string, where)
        return parse
    
class ArrayConstraint(Contract):
    ''' Comparisons for numpy array elements. They check that
        the condition is respected for all the entries in the array. '''
    
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
        assert isinstance(rvalue, RValue)  
        Contract.__init__(self, where)
        self.glyph = glyph 
        self.rvalue = rvalue
        self.op = ArrayConstraint.constraints[glyph]
        
        
    def check_contract(self, context, value):
        assert isinstance(value, ndarray)
        bound = context.eval(self.rvalue, self)

        result = self.op(value, bound)
        
        ok = numpy.all(result)
        
        if not ok:
            # count the number of invalid:
            num_fail = numpy.sum(1 * value.flatten())
            num = value.size
            perc = 100.0 * num_fail / num
            error = ('%d/%d (%f%%) of elements do not respect the condition '
                     ' "x %s %s". ' % 
                     (num_fail, num, perc, self.glyph, bound))
            # TODO: display some of those values?
            raise ContractNotRespected(self, error, value, context)
     
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

supported = ("uint8 uint16 uint32 uint64 int8 int16 int32 int64 float32 float64"
             " u1 i1")
       
dtype_checks = []
for x in supported.split():
    d = numpy.dtype(x)
    expr = Keyword(x).setParseAction(DType.parse_action(d))  
    dtype_checks.append(expr)

ndarray_simple_contract = MatchFirst(dtype_checks + array_constraints)
ndarray_simple_contract.setName('numpy element contract')


suggester = create_suggester(get_options=lambda:supported.split())
baseExpr = ndarray_simple_contract | suggester
baseExpr.setName('numpy contract (with recovery)')

operatorPrecedence = myOperatorPrecedence
ndarray_composite_contract = operatorPrecedence(baseExpr, [
                        (',', 2, opAssoc.LEFT, And.parse_action),
                         ('|', 2, opAssoc.LEFT, OR.parse_action),
                    ])


def my_delim_list2(what, delim): 
    return (what + ZeroOrMore(S(delim) + FollowedBy(NotAny(ellipsis)) - what))
ellipsis = Literal('...')

shape_suggester = create_suggester(get_options=lambda:['...'],
                                   pattern=Word('.'))

inside_inside1 = simple_contract | shape_suggester
inside_inside2 = contract | shape_suggester
inside = (S('(') - inside_inside2 - S(')')) | inside_inside1 # XXX: ^ and use or_contract?
shape_contract = my_delim_list2(inside, S('x')) + O(S('x') + ellipsis)
shape_contract.setParseAction(ShapeContract.parse_action)
shape_contract.setName('array shape contract')

name = S('array') | S('ndarray')
optional_shape = (S('[') - shape_contract - S(']'))('shape_contract')
optional_elements = (S('(') - ndarray_composite_contract - S(')'))('elements_contract')
array_contract = name + O(optional_shape) + O(optional_elements)
array_contract.setParseAction(Array.parse_action)
array_contract.setName('array() contract')
add_contract(array_contract)
add_keyword('array')
add_keyword('ndarray')

optional_length = (S('[') - contract - S(']'))('length')
optional_other = (S('(') - contract - S(')'))('other')
shape = S('shape') + O(optional_length) + O(optional_other)
shape.setName('shape() contract')
shape.setParseAction(Shape.parse_action)
add_contract(shape)
add_keyword('shape')
