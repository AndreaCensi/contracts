from ..interface import Contract, ContractNotRespected, RValue
from ..syntax import W
from ..interface import eval_in_context


class EqualTo(Contract):
    def __init__(self, rvalue, where=None):
        Contract.__init__(self, where)
        assert isinstance(rvalue, RValue), "Expected RValue for EqualTo, got %r" % rvalue
        self.rvalue = rvalue

    def check_contract(self, context, value, silent):
        val = eval_in_context(context, self.rvalue, self)
        if not(val == value):
            error = ('EqualTo: Condition %s == %s not respected.'
                     % (val, value))
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
        from contracts.library.types_misc import CheckType
        if isinstance(rvalue, CheckType):
            return rvalue
        else:
            assert isinstance(rvalue, RValue)
            return EqualTo(rvalue, where)


class SimpleRValue(RValue):
    def __init__(self, value, representation=None, where=None):
        assert representation is None or isinstance(representation, str)
        self.value = value
        self.where = where
        self.representation = representation

    def __str__(self):
        if self.representation is None:
            return "{0!s}".format(self.value)
        else:
            return self.representation

    def __repr__(self):
        if self.representation is None:
            return "SimpleRValue({0!r})".format(self.value)
        else:
            return "SimpleRValue({0!r},{1!r})".format(self.value,
                                                      self.representation)

    def eval(self, context):  # @UnusedVariable @ReservedAssignment
        return self.value


