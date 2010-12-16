from contracts.interface import Contract, ContractSemanticError, RValue
from contracts.syntax import isnumber, W, add_rvalue, add_contract, rvalue, Literal, \
    S
from contracts.library.comparison import CheckOrder
from pyparsing import operatorPrecedence, opAssoc

class DoArithmetic(RValue):
    
    def __init__(self, where, expr1, expr2, operation, glyph):
        self.where = where
        self.expr1 = expr1
        self.expr2 = expr2
        self.operation = operation
        self.glyph = glyph
        
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
        s = 'DoArithmetic(%r,%s,%r)' % (self.expr1, self.glyph, self.expr2)
        return s
    
    def __str__(self):
        s = '%s%s%s' % (self.expr1, self.glyph, self.expr2)
        return s
    


def parse_arithmetic_rvalue(operation, glyph):
    def parse_arithmetic_rvalue2(s, loc, tokens):
        where = W(s, loc)
        expr1 = tokens[0][0]
        expr2 = tokens[0][2]
        #expr1 = tokens['expr1']
        #expr2 = tokens['expr2']
        for e in [expr1, expr2]:
            assert isnumber(e) or isinstance(e, RValue)
        return DoArithmetic(where, expr1, expr2, operation, glyph)
    
    return parse_arithmetic_rvalue2

def parse_arithmetic_as_contract(operation, glyph):
    def parse_arithmetic2(s, loc, tokens):
        where = W(s, loc)
        rvalue = parse_arithmetic_rvalue(operation, glyph)(s, loc, tokens)
        return CheckOrder(where, None, rvalue, False, True, False)
    return parse_arithmetic2 

# TODO: precedence
#
#operations = {
#    '+': lambda x, y: x + y,
#    '-': lambda x, y: x - y,
#    '*': lambda x, y: x * y,
#}
#
#expr = operatorPrecedence(rvalue,
#    [
#     ('*', 2, opAssoc.LEFT),
#     ('+', 2, opAssoc.LEFT), ]
#    )
#add_rvalue(expr)
#
#
#for glyph, operation in operations.items():
#    expr = rvalue('expr1') + S(Literal(glyph)) + rvalue('expr2')
#    as_rvalue = expr.copy().setParseAction(parse_arithmetic_rvalue(operation, glyph)) 
#    #add_rvalue(as_rvalue) 
#    as_contract = expr.copy().setParseAction(parse_arithmetic_as_contract(operation, glyph)) 
#    #add_contract(as_contract) 
        
