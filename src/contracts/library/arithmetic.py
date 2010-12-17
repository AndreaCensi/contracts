from contracts.interface import ContractSemanticError, RValue
from contracts.syntax import (isnumber, W)

class DoArithmetic(RValue):
    operations = {
        '+': lambda x, y: x + y,
        '-': lambda x, y: x - y,
        '*': lambda x, y: x * y
    }
    def __init__(self, where, expr1, expr2, glyph):
        self.where = where
        self.expr1 = expr1
        self.expr2 = expr2
        #self.operation = operation
        self.glyph = glyph
        self.operation = DoArithmetic.operations[glyph]
        
    def eval(self, context):
        val1 = context.eval(self.expr1, self)            
        val2 = context.eval(self.expr2, self)

        for val in [val1, val2]:
            if not isnumber(val):
                msg = ('I can only do math with numbers, not %r.' % 
                       val.__class__.__name__) 
                raise ContractSemanticError(self, msg, context)
        
        return self.operation(val1, val2)
        
    def __repr__(self):
        s = 'DoArithmetic(%r,%r,%r)' % (self.expr1, self.glyph, self.expr2)
        return s
    
    def __str__(self):
        s = '(%s%s%s)' % (self.expr1, self.glyph, self.expr2)
        return s

def parse_arithmetic_rvalue_simpler(s, loc, tokens):
    where = W(s, loc)
    expr1 = tokens[0][0]
    glyph = tokens[0][1]
    expr2 = tokens[0][2]
    for e in [expr1, expr2]:
        assert isnumber(e) or isinstance(e, RValue)
    return DoArithmetic(where, expr1, expr2, glyph)
    
def parse_arithmetic_rvalue(glyph):
    def parse_arithmetic_rvalue2(s, loc, tokens):
        where = W(s, loc)
        expr1 = tokens[0][0]
    #    glyph = tokens[0][1]
        expr2 = tokens[0][2]
        for e in [expr1, expr2]:
            assert isnumber(e) or isinstance(e, RValue)
        return DoArithmetic(where, expr1, expr2, glyph)
    
    return parse_arithmetic_rvalue2

def parse_unary_minus(s, loc, tokens):
    where = W(s, loc)
    expr1 = 0
    glyph = tokens[0][0]
    expr2 = tokens[0][1]
    assert glyph in ['+', '-']
    #operation = 
    for e in [expr1, expr2]:
        assert isnumber(e) or isinstance(e, RValue)
    return DoArithmetic(where, expr1, expr2, '-')
    
