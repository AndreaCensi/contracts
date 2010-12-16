from contracts.interface import Contract, ContractNotRespected, VariableRef, \
    ContractSemanticError
from contracts.syntax import W, add_contract, rvalues
from pyparsing import Literal
from contracts.library.variables import variables
from contracts.library.lists import O

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
        
    def check_contract(self, context, value):
        if self.expr1 is None:
            val1 = value
        else:
            val1 = context.eval(self.expr1, self)
            
        number = (int, float)
            
        val2 = context.eval(self.expr2, self)

        for val in [val1, val2]:
            if not isinstance(val, number):
                msg = ('I can only compare numbers, not %r.' % 
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
    
    def __repr__(self):
        if self.expr1:
            return '%s%s%s' % (self.expr1, self.glyph, self.expr2)
        else:
            return '%s%s' % (self.glyph, self.expr2)
    
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

variable_ref = variables.copy()

def create_var_ref(s, loc, tokens):
    where = W(s, loc)
    return VariableRef(where, tokens[0])

variable_ref.setParseAction(create_var_ref)

comparable = rvalues ^ variable_ref 

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
    expr = O(comparable('expr1')) + Literal(glyph) + comparable('expr2')
    expr.setParseAction(CheckOrder.parse_action(condition[0],
                                                condition[1],
                                                condition[2]))
    add_contract(expr)




