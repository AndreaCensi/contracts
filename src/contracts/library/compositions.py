from ..syntax import simple_contract, W, OneOrMore, Suppress
from ..interface import Contract, ContractNotRespected
from pyparsing import operatorPrecedence, opAssoc

class Logical():
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

    def str_logical(self, environment_precedence=1):
        pass

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

        msg = 'No clause could be satisfied. Details:'
        for c, e in exceptions:
            msg += '\n- %20s: %s' % (c, e)
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
            glyph = l.pop(0)
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
            glyph = l.pop(0)
            operand = l.pop(0)
            clauses.append(operand)
#            
#        print tokens
#        expr1 = tokens[0][0]
#        glyph = tokens[0][1]
#        expr2 = tokens[0][2]
#        clauses = [expr1, expr2]
##        for c in tokens:
##            assert isinstance(c, Contract), 'Wrong class %r' % c
#            clauses.append(c)
        where = W(string, location)
        return And(clauses, where=where)


#def at_least_2_delim_list(what, delim): 
#    return (what + OneOrMore(Suppress(delim) + what))
#
#and_op = at_least_2_delim_list(simple_contract, ',') 
#and_op.setParseAction(And.parse_action)
#
#or_op = at_least_2_delim_list(simple_contract, '|') 
#or_op.setParseAction(OR.parse_action)

composite_contract = operatorPrecedence(simple_contract,
    [
     (',', 2, opAssoc.LEFT, And.parse_action),
     ('|', 2, opAssoc.LEFT, OR.parse_action),
    ]
)

#composite_contract = or_op ^ and_op # FIXME: Are you sure? parenthesis/precedence 
