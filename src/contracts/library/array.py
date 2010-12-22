import numpy
from numpy  import ndarray, dtype #@UnusedImport

from ..interface import Contract, ContractNotRespected, RValue
from ..syntax import (add_contract, W, contract, O, S, rvalue,
                      get_or, simple_contract, ZeroOrMore, Literal)


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
        s = 'x'.join("%s" % x for x in self.dimensions)
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
        glyph = tokens['glyph']
        rvalue = tokens['rvalue']
        return ArrayConstraint(glyph, rvalue, where)
 

array_constraints = []
for glyph in ArrayConstraint.constraints:
    expr = Literal(glyph)('glyph') + rvalue('rvalue')
    expr.setParseAction(ArrayConstraint.parse_action)
    array_constraints.append(expr)

dtype_checks = []
for x in ['u1', 'i1', 'uint8', 'int8', 'float32', 'float64']:
    d = numpy.dtype(x)
    expr = Literal(x).setParseAction(DType.parse_action(d))  
    dtype_checks.append(expr)
 
ndarray_contract = get_or(dtype_checks) | get_or(array_constraints)

def my_delim_list2(what, delim): 
    return (what + ZeroOrMore(S(delim) + what))

ellipsis = Literal('...')

inside = simple_contract ^ (S('(') + simple_contract + S(')'))
shape_contract = (my_delim_list2(inside, S('x')) + O(S('x') + ellipsis))
shape_contract.setParseAction(ShapeContract.parse_action)


name = S('array') | S('ndarray')
optional_shape = (S('[') + shape_contract + S(']'))('shape_contract')
optional_elements = (S('(') + ndarray_contract + S(')'))('elements_contract')
array_contract = name + O(optional_shape) + O(optional_elements)
                   
array_contract.setParseAction(Array.parse_action)
add_contract(array_contract)


optional_length = (S('[') + contract + S(']'))('length')
optional_other = (S('(') + contract + S(')'))('other')
shape = S('shape') + O(optional_length) + O(optional_other)
                                            
shape.setParseAction(Shape.parse_action)
add_contract(shape)

#add_alias('rgb', 'array[HxWx3](uint8),H>0,W>0')
#add_alias('rgba', 'array[HxWx4](uint8),H>0,W>0')
#
#add_alias('correlation', 'array[NxN]((float32|float64),>=-1,<=1),diagonal(=1),posdef')


