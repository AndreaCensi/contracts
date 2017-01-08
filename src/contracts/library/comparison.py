import math

from pyparsing import Or

from ..interface import Contract, ContractNotRespected, RValue, eval_in_context
from ..syntax import W, add_contract, O, Literal, isnumber, rvalue


class CheckOrder(Contract):

    conditions = {
        '=': (False, True, False),  # smaller, equal, larger flags
        '==': (False, True, False),
        '!=': (True, False, True),
        '>': (False, False, True),
        '>=': (False, True, True),
        '<': (True, False, False),
        '<=': (True, True, False)
    }

    def __init__(self, expr1, glyph, expr2, where=None):
        Contract.__init__(self, where)
        assert isinstance(expr1, RValue) or expr1 is None
        assert isinstance(expr2, RValue)

        self.expr1 = expr1
        self.glyph = glyph
        self.expr2 = expr2
        self.smaller, self.equal, self.larger = CheckOrder.conditions[glyph]

    def check_contract(self, context, value, silent):
        if self.expr1 is None:
            val1 = value
        else:
#            val1 = context.eval(self.expr1, self)
            val1 = eval_in_context(context, self.expr1, self)

#        val2 = context.eval(self.expr2, self)
        val2 = eval_in_context(context, self.expr2, self)

        # Check if we only need to check equality
        # in that case, we don't care for the type

        # FIXME: add support for != here
        pure_equality = (
            (self.smaller, self.equal, self.larger) == (False, True, False)
            or
            (self.smaller, self.equal, self.larger) == (True, False, True))

        if pure_equality:
            # but we want them to be either numbers or same type
            if (not (isnumber(val1) and isnumber(val2))) and \
                (not isinstance(val1, val2.__class__)):
                msg = ("I won't let you compare two different types if they "
                       "are not numbers (%s,%s)" % (type(val1), type(val2)))
                raise ContractNotRespected(self, msg, (val1, val2), context)

            ok = (val1 == val2) ^ (not self.equal)
        else:
            # We potentially want < or >. They must be numbers.

            for val in [val1, val2]:
                if not isnumber(val):
                    msg = ('I can only compare the order of numbers, not %r.' %
                           val.__class__.__name__)
                    raise ContractNotRespected(self, msg, (val1, val2),
                                               context)

            if math.isnan(val1) or math.isnan(val2):
                msg = ('I cannot compare NaN (checking: %s %s %s)'
                       % (val1, self.glyph, val2))
                raise ContractNotRespected(self, msg, (val1, val2), context)

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
        if self.expr1 is not None:
            return '%s%s%s' % (self.expr1, self.glyph, self.expr2)
        else:
            return '%s%s' % (self.glyph, self.expr2)

    def __repr__(self):
        return 'CheckOrder(%r,%r,%r)' % (self.expr1, self.glyph, self.expr2)

    @staticmethod
    def parse_action(s, loc, tokens):
        expr1 = tokens.get('expr1', None)
        glyph = "".join(tokens['glyph'])
        expr2 = tokens['expr2']
        where = W(s, loc)
        return CheckOrder(expr1, glyph, expr2, where=where)


comparisons_expr = {}
for glyph in CheckOrder.conditions:
    if glyph == '!=':
        # special case: ! must be followed by =
        glyph_expression = Literal('!') - Literal('=')
        glyph_expression.setName('!=')
    else:
        glyph_expression = Literal(glyph)

    # 2015-05: not sure why this doesn't work and the alternative with + does
    # expr = O(rvalue('expr1')) + glyph_expression('glyph') - rvalue('expr2')
    expr = O(rvalue('expr1')) + glyph_expression('glyph') + rvalue('expr2')

    expr.setParseAction(CheckOrder.parse_action)
    add_contract(expr)

    comparisons_expr[glyph] = expr


comparison_expr = Or(exprs=list(comparisons_expr.values()))
