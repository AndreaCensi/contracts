from ..syntax import simple_contract, W, operatorPrecedence, opAssoc
from ..interface import Contract, ContractNotRespected, add_prefix

class Logical(object):
    def __init__(self, glyph, precedence):
        self.glyph = glyph
        self.precedence = precedence
         
    def __str__(self):
        def convert(x):
            if isinstance(x, Logical) and x.precedence < self.precedence:
                return '(%s)' % x
            else:
                return '%s' % x

        s = self.glyph.join(convert(x) for x in self.clauses)
        return s


class OR(Logical, Contract):
    def __init__(self, clauses, where=None):
        assert isinstance(clauses, list) and len(clauses) >= 2
        Contract.__init__(self, where)
        Logical.__init__(self, '|', 1)
        self.clauses = clauses
        
    def check_contract(self, context, value):
        exceptions = []
        for c in self.clauses:
            try:
                # try with fake context
                c._check_contract(context.copy(), value)
                # if ok, do with main context
                c._check_contract(context, value)
                return
            except ContractNotRespected as e:
                exceptions.append((c, e))

        msg = 'Could not satisfy any of the %d clauses.' % len(self.clauses)
        
        for i, ex in enumerate(exceptions):
            c, e = ex
            msg += '\n---- Clause #%d: ----\n' % i 
            msg += add_prefix('%s' % e, '| ')

        msg += '\n------- (end clauses) -------'
        raise ContractNotRespected(contract=self, error=msg,
                    value=value, context=context)

    def __repr__(self):
        s = 'OR(%r)' % self.clauses
        return s

    @staticmethod
    def parse_action(string, location, tokens):
        l = list(tokens[0])
        clauses = [l.pop(0)]
        while l:
            glyph = l.pop(0) #@UnusedVariable
            assert glyph == '|'
            operand = l.pop(0)
            clauses.append(operand)
        where = W(string, location)
        return OR(clauses, where=where)
        

class And(Logical, Contract):
    def __init__(self, clauses, where=None):
        assert isinstance(clauses, list) and len(clauses) >= 2
        Contract.__init__(self, where)
        Logical.__init__(self, ',', 2)
        self.clauses = clauses
    
    def check_contract(self, context, value):
        for c in self.clauses:
            c._check_contract(context, value)

    def __repr__(self):
        s = 'And(%r)' % self.clauses
        return s

    @staticmethod
    def parse_action(string, location, tokens):
        l = list(tokens[0])
        clauses = [l.pop(0)]
        while l:
            glyph = l.pop(0) #@UnusedVariable
            assert glyph == ','
            operand = l.pop(0)
            clauses.append(operand)
        where = W(string, location)
        return And(clauses, where=where)


composite_contract = operatorPrecedence(simple_contract, [
                         (',', 2, opAssoc.LEFT, And.parse_action),
                         ('|', 2, opAssoc.LEFT, OR.parse_action),
                    ])
or_contract = operatorPrecedence(simple_contract, [
                         ('|', 2, opAssoc.LEFT, OR.parse_action),
                    ])
 
