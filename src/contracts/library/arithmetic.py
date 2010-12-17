from contracts.interface import ContractSemanticError, RValue
from contracts.syntax import (isnumber, W)

class Binary(RValue):
    operations = {
        '+': lambda x, y: x + y,
        '-': lambda x, y: x - y,
        '*': lambda x, y: x * y
    }
    
    precedence = {
        '+': 0,
        '-': 0,
        '*': 1,
    }
    def __init__(self, where, expr1, expr2, glyph):
        self.where = where
        self.expr1 = expr1
        self.expr2 = expr2 
        self.glyph = glyph
        self.operation = Binary.operations[glyph]
        self.precedence = Binary.precedence[glyph]
        
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
        s = 'Binary(%r,%r,%r)' % (self.expr1, self.glyph, self.expr2)
        return s
    
    def __str__(self):
        def convert(x):
            if isinstance(x, Binary) and x.precedence < self.precedence:
                return '(%s)' % x
            else:
                return '%s' % x
        
        s = '%s%s%s' % (convert(self.expr1), self.glyph, convert(self.expr2))
        return s

    @staticmethod
    def parse_action(s, loc, tokens):
        where = W(s, loc)
        expr1 = tokens[0][0]
        glyph = tokens[0][1]
        expr2 = tokens[0][2]
        for e in [expr1, expr2]:
            assert isnumber(e) or isinstance(e, RValue)
        return Binary(where, expr1, expr2, glyph)


class Unary(RValue):
    operations = {
        '-': lambda x:-x,
    }
    def __init__(self, glyph, expr, where=None):
        self.where = where
        self.expr = expr
        self.glyph = glyph
        self.operation = Unary.operations[glyph]
        #self.precedence = DoArithmetic.precedence[glyph]
        
    def eval(self, context):
        val = context.eval(self.expr, self)
        if not isnumber(val):
            msg = ('I can only do math with numbers, not %r.' % 
                   val.__class__.__name__) 
            raise ContractSemanticError(self, msg, context)
        
        return self.operation(val)
        
    def __repr__(self):
        s = 'Unary(%r,%r)' % (self.glyph, self.expr)
        return s
    
    def __str__(self): 
        # XXX
        return '%s%s' % (self.glyph, self.expr)
    
    @staticmethod
    def parse_action(s, loc, tokens):
        where = W(s, loc)
        glyph = tokens[0][0]
        expr = tokens[0][1]
        return Unary(glyph, expr, where)
    
