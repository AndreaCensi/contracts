from pyparsing import delimitedList, OneOrMore, Suppress
from .syntax import simple_contract, W
from .interface import Contract, ContractNotRespected


class OR(Contract):
    def __init__(self, where, clauses):
        assert len(clauses) > 0
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

    @staticmethod
    def parse_action(string, location, tokens):
        clauses = []
        for c in tokens:
            assert isinstance(c, Contract), 'Wrong class %r' % c
            clauses.append(c)
        return OR(W(string, location), clauses)

# AND operator
class And(Contract):
    def __init__(self, where, clauses):
        assert len(clauses) >= 2
        Contract.__init__(self, where)
        self.clauses = clauses
    
    def check_contract(self, context, value):
        for c in self.clauses:
            c.check_contract(context, value)

    @staticmethod
    def parse_action(string, location, tokens):
        clauses = []
        for c in tokens:
            assert isinstance(c, Contract), 'Wrong class %r' % c
            clauses.append(c)
        return And(W(string, location), clauses)

    def __repr__(self):
        s = ', '.join(x.__repr__() for x in self.clauses)
        return s


def at_least_2_delim_list(what, delim): 
    return (what + OneOrMore(Suppress(delim) + what))

and_op = at_least_2_delim_list(simple_contract, ',') 
and_op.setParseAction(And.parse_action)

or_op = at_least_2_delim_list(simple_contract, '|') 
or_op.setParseAction(OR.parse_action)

composite_contract = or_op ^ and_op
