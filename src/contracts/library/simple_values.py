from ..interface import Contract, ContractNotRespected, RValue
from ..syntax import W


class EqualTo(Contract):
    def __init__(self, rvalue, where=None):
        Contract.__init__(self, where)
        assert isinstance(rvalue, RValue)
        self.rvalue = rvalue
        
    def check_contract(self, context, value):
        val = context.eval(self.rvalue, self)
        if not(val == value):
            error = ('EqualTo: Condition %s == %s not respected.' % (val, value))
            raise ContractNotRespected(contract=self, error=error,
                                       value=value, context=context)    
    def __str__(self):
        return "%s" % self.rvalue
        
    def __repr__(self):
        return 'EqualTo(%r)' % self.rvalue
    
    @staticmethod
    def parse_action(s, loc, tokens):
        where = W(s, loc)
        rvalue = tokens[0]
        return EqualTo(rvalue, where)
