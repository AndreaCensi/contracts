from contracts.interface import Contract, ContractNotRespected, \
    ContractSemanticError, RValue
from contracts.syntax import W, add_contract, O, Literal, isnumber, rvalue
 
class CheckOrder(Contract):
    
    def __init__(self, where, expr1, expr2, smaller, equal, larger):
        Contract.__init__(self, where)
        self.expr1 = expr1
        self.expr2 = expr2
        self.larger = larger
        self.equal = equal
        self.smaller = smaller
        assert isinstance(larger, bool)
        assert isinstance(equal, bool)
        assert isinstance(smaller, bool)
        self.glyph = glyphs[(smaller, equal, larger)]
        
        for s in [expr1, expr2]:
            assert s is None or isnumber(s) or isinstance(s, RValue)  
        
    def check_contract(self, context, value):
        if self.expr1 is None:
            val1 = value
        else:
            val1 = context.eval(self.expr1, self)
                    
        val2 = context.eval(self.expr2, self)
 
        # Check if we only need to check equality
        # in that case, we don't care for the type
        if (self.smaller, self.equal, self.larger) == (False, True, False):
            # but we want them to be either numbers or same type
            if (not (isnumber(val1) and isnumber(val2))) and \
                type(val1) != type(val2):
                msg = ("I won't let you compare two different types if they "
                       "are not numbers (%s,%s)" % (type(val1), type(val2))) 
                raise ContractSemanticError(self, msg, context)
        
            ok = (val1 == val2)
        else:
            # We potentially want < or >. They must be numbers.
    
            for val in [val1, val2]:
                if not isnumber(val):
                    msg = ('I can only compare the order of numbers, not %r.' % 
                           val.__class__.__name__) 
                    raise ContractSemanticError(self, msg, context)
            
            if val1 < val2:
                ok = self.smaller
            elif val1 > val2:
                ok = self.larger
            else:
                assert val1 == val2
                ok = self.equal
            
        if not ok:
            error = ('Condition %s %s %s not respected' % 
                    (val1, self.glyph, val2))
            
            raise ContractNotRespected(contract=self, error=error,
                                       value=value, context=context)
    
    def __str__(self):
        if self.expr1:
            return '%s%s%s' % (self.expr1, self.glyph, self.expr2)
        else:
            return '%s%s' % (self.glyph, self.expr2)
        
    def __repr__(self):
        return 'CheckOrder(%r,%r,%r)' % (self.expr1, self.glyph, self.expr2)
    
    @staticmethod
    def parse_action(smaller, equal, larger):
        def parse(s, loc, tokens):
            if 'expr1' in tokens:
                expr1 = tokens['expr1']
            else:
                expr1 = None
            expr2 = tokens['expr2']
            where = W(s, loc)
            return CheckOrder(where, expr1, expr2, smaller, equal, larger)
        return parse 


glyphs = {
    (False, True, False): '=',
    (True, False, True): '!=',
    (False, False, True): '>',
    (False, True, True): '>=',
    (True, False, False): '<',
    (True, True, False): '<='          
}

combinations = list(glyphs.items()) + [((False, True, False), '==')]

for condition, glyph in combinations:
    expr = O(rvalue('expr1')) + Literal(glyph) + rvalue('expr2')
    expr.setParseAction(CheckOrder.parse_action(condition[0],
                                                condition[1],
                                                condition[2]))
    add_contract(expr)




