from ..interface import Contract, ContractNotRespected, add_prefix
from ..pyparsing_utils import myOperatorPrecedence
from ..syntax import ParsingTmp, W, opAssoc, simple_contract
from .extensions import Extension
from .suggester import create_suggester


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
        assert isinstance(clauses, list)
        assert len(clauses) >= 2
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
                break
            except ContractNotRespected as e:
                exceptions.append((c, e))
        else:
            msg = ('Could not satisfy any of the %d clauses in %s.'
                   % (len(self.clauses), self))

            for i, ex in enumerate(exceptions):
                c, e = ex
                msg += '\n ---- Clause #%d:   %s\n' % (i + 1, c)
                msg += add_prefix('%s' % e, ' | ')

            msg += '\n ------- (end clauses) -------'
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
            glyph = l.pop(0)  # @UnusedVariable
            assert glyph == '|'
            operand = l.pop(0)
            clauses.append(operand)
        where = W(string, location)
        return OR(clauses, where=where)


class And(Logical, Contract):
    def __init__(self, clauses, where=None):
        assert isinstance(clauses, list)
        assert len(clauses) >= 2, clauses
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
            glyph = l.pop(0)  # @UnusedVariable
            assert glyph == ','
            operand = l.pop(0)
            clauses.append(operand)
        where = W(string, location)
        return And(clauses, where=where)


suggester = create_suggester(get_options=lambda: ParsingTmp.keywords +
                             list(Extension.registrar.keys()))
baseExpr = simple_contract | suggester
baseExpr.setName('Simple contract (recovering)')

composite_contract = myOperatorPrecedence(baseExpr, [
                         (',', 2, opAssoc.LEFT, And.parse_action),
                         ('|', 2, opAssoc.LEFT, OR.parse_action),
                    ])
composite_contract.setName('OR/AND contract')

or_contract = myOperatorPrecedence(baseExpr, [
                         ('|', 2, opAssoc.LEFT, OR.parse_action),
                    ])
or_contract.setName('OR contract')

