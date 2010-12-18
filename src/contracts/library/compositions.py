from ..syntax import simple_contract, W, OneOrMore, Suppress
from ..interface import Contract, ContractNotRespected


class OR(Contract):
    def __init__(self, clauses, where=None):
        assert isinstance(clauses, list) and len(clauses) >= 2
        Contract.__init__(self, where)
        self.clauses = clauses
    
    def check_contract(self, context, value):
        exceptions = []
        for c in self.clauses:
            try:
                # try with fake context
                c.check_contract(context.copy(), value)
                # if ok, do with main context
                c.check_contract(context, value)
                return
            except ContractNotRespected as e:
                exceptions.append((c, e))

        msg = 'No clause could be satisfied. Details:'
        for c, e in exceptions:
            msg += '\n- %20s: %s' % (c, e)
        raise ContractNotRespected(contract=self, error=msg,
                    value=value, context=context)

    def __str__(self):
        s = '|'.join("%s" % x for x in self.clauses)
        return s

    def __repr__(self):
        #s = 'OR(%s)' % ",".join("%r" % x for x in self.clauses)
        s = 'OR(%r)' % self.clauses
        return s

    @staticmethod
    def parse_action(string, location, tokens):
        clauses = []
        for c in tokens:
            assert isinstance(c, Contract), 'Wrong class %r' % c
            clauses.append(c)
        where = W(string, location)
        return OR(clauses, where=where)
        
# AND operator
class And(Contract):
    def __init__(self, clauses, where=None):
        assert isinstance(clauses, list) and len(clauses) >= 2
        Contract.__init__(self, where)
        self.clauses = clauses
    
    def check_contract(self, context, value):
        for c in self.clauses:
            c.check_contract(context, value)

    def __str__(self):
        s = ','.join("%s" % x for x in self.clauses)
        return s

    def __repr__(self):
        #s = 'And(%s)' % ",".join("%r" % x for x in self.clauses)
        s = 'And(%r)' % self.clauses
        return s

    @staticmethod
    def parse_action(string, location, tokens):
        clauses = []
        for c in tokens:
            assert isinstance(c, Contract), 'Wrong class %r' % c
            clauses.append(c)
        where = W(string, location)
        return And(clauses, where=where)


def at_least_2_delim_list(what, delim): 
    return (what + OneOrMore(Suppress(delim) + what))

and_op = at_least_2_delim_list(simple_contract, ',') 
and_op.setParseAction(And.parse_action)

or_op = at_least_2_delim_list(simple_contract, '|') 
or_op.setParseAction(OR.parse_action)

composite_contract = or_op ^ and_op # FIXME: Are you sure? parenthesis/precedence 
