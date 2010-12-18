from ..interface import Contract, ContractNotRespected
from ..syntax import add_contract, W, contract, O, S
from numpy  import ndarray
from contracts.syntax import S, isnumber, rvalue, get_or, simple_contract
from pyparsing import ZeroOrMore, Literal
import numpy
from contracts.interface import RValue
from pyparsing import stringEnd

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
            self.shape_contract.check_contract(context, value.shape)
        
        if self.elements_contract is not None:
            self.elements_contract.check_contract(context, value)
    
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
        shape_contract = tokens.get('shape_contract', None)
        elements_contract = tokens.get('elements_contract', None)
        return Array(shape_contract, elements_contract, where=where)


class ShapeContract(Contract):
    def __init__(self, dimensions, ellipsis, where=None):
        Contract.__init__(self, where)
        self.dimensions = dimensions
        self.ellipsis = ellipsis
    
    def check_contract(self, context, value):
        if not isinstance(value, tuple):
            assert False, 'Expected a tuple got %r.' % value.__class__.__name__

        expected = len(self.dimensions)
        ndim = len(value)
        if ndim < expected:
            error = 'Expected %d dimensions, got %d.' % (expected, ndim)
            raise ContractNotRespected(contract=self, error=error,
                                       value=value, context=context)
        if ndim > expected and not ellipsis:
            error = 'Expected %d dimensions, got %d.' % (expected, ndim) 
            raise ContractNotRespected(contract=self, error=error,
                                       value=value, context=context)
        
        for i in range(expected):
            self.dimensions.check_contract(context, value[i])
    
    def __str__(self):
        s = 'x'.join("%s" % x for x in self.dimensions)
        if self.ellipsis:
            s += 'x...'
        return s
    
    def __repr__(self):
        s = 'ShapeContract(%r,%r)' % (self.dimensions, self.ellipsis)
        return s
    
    @staticmethod 
    def parse_action(s, loc, tokens):
        where = W(s, loc)
        dimensions = list(tokens.get('dimensions'))
        ellipsis = 'ellipsis' in tokens
        sc = ShapeContract(dimensions, ellipsis, where=where)
        print "Parsed %r" % sc
        return sc

class Shape(Contract):
    def __init__(self, length, contract, where=None):
        Contract.__init__(self, where)
        self.contract = contract
        self.length = length
    
    def check_contract(self, context, value):
        if not isinstance(value, (ndarray, tuple)):
            assert False, 'Expected an array, got %r.' % value.__class__.__name__
        if isinstance(value, ndarray):
            value = value.shape
        if self.length is not None:
            self.length.check_contract(context, len(value))
            
        if self.contract is not None:
            self.contract.check_contract(context, value)
    
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
#        print "Got tokens: ", tokens
        length = tokens.get('length', None)
        contract = tokens.get('contract', None)
#        print "found length = %r" % length
#        print "found contract = %r" % contract
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
        if not isinstance(value, ndarray):
            assert False, 'Expected an array, got %r.' % value.__class__.__name__
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
        Contract.__init__(self, where)
        self.glyph = glyph 
        self.rvalue = rvalue
        self.op = ArrayConstraint.constraints[glyph]
        
        # TODO: make numbers into RValues
        assert isnumber(rvalue) or isinstance(rvalue, RValue)  
        
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
for x in ['uint8', 'int8', 'float32', 'float64']:
    d = numpy.dtype(x)
    expr = Literal(x).setParseAction(DType.parse_action(d))  
    dtype_checks.append(expr)
 
ndarray_contract = get_or(dtype_checks) | get_or(array_constraints)

def my_delim_list(what, delim): 
    return (what + ZeroOrMore(S(delim) + what))

ellipsis = Literal('...')
delim = Literal('x') ^ Literal(',')
shape_contract = my_delim_list(simple_contract, delim)('dimensions') + \
    O(S(delim) + ellipsis('ellipsis')) #+ stringEnd 
shape_contract.setParseAction(ShapeContract.parse_action)

shape = S('shape') + O(S('[') + contract('length') + S(']')) + \
            O(S('(') + shape_contract('contract') + S(')'))  
shape.setParseAction(Shape.parse_action)
add_contract(shape)

array_contract = ((S('array') | S('ndarray')) + 
                 O(S('[') + (shape | shape_contract)('shape_contract') + S(']')) + 
                 O(S('(') + ndarray_contract('elements_contract') + S(')')))
array_contract.setParseAction(Array.parse_action)
add_contract(array_contract)



#add_alias('rgb', 'array[HxWx3](uint8),H>0,W>0')
#add_alias('rgba', 'array[HxWx4](uint8),H>0,W>0')
#
#add_alias('correlation', 'array[NxN]((float32|float64),>=-1,<=1),diagonal(=1),posdef')


