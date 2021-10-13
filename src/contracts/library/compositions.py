#cython: language_level=3, annotation_typing=True, c_string_encoding=utf-8, boundscheck=False, wraparound=False, initializedcheck=False

from ..interface import Contract, ContractNotRespected, add_prefix
from ..pyparsing_utils import myOperatorPrecedence
from ..syntax import ParsingTmp, W, opAssoc, simple_contract
from .extensions import Extension
from .suggester import create_suggester

NOT_GLYPH = '!'
AND_GLYPH = ','
OR_GLYPH = '|'

class Logical(object):
    def __init__(self, glyph, precedence):
        self.glyph = glyph
        self.precedence = precedence

    def __str__(self):
        s = self.glyph.join(self._convert(x) for x in self.clauses)
        return s

    def _convert(self, x):
        if isinstance(x, Logical) and x.precedence < self.precedence:
            return '(%s)' % x
        return '%s' % x

class OR(Logical, Contract):
    def __init__(self, clauses, where=None):
        assert isinstance(clauses, list)
        assert len(clauses) >= 2
        Contract.__init__(self, where)
        Logical.__init__(self, OR_GLYPH, 1)
        self.clauses = clauses

    def _check_quick(self, context, value):
        """ Returns True if this checks out. """

        # first make a quick pass
        for c in self.clauses:
            try:
                # try with fake context
                c._check_contract(context.copy(), value, silent=True)
                # if ok, do with main context
                c._check_contract(context, value, silent=True)
                return True
            except ContractNotRespected as e:
                pass
        
        return False


    def check_contract(self, context, value, silent):
        orig = context.copy()

        if self._check_quick(context, value):
            return
        else:
            if silent:
                msg = '(Error description suppressed.)'
                raise ContractNotRespected(contract=self, error=msg,
                        value=value, context=context)

            # otherwise need to do it again with detailed error messages
            self.get_error(orig, value)

    def get_error(self, context, value):
        """ This assumes that we are going to fail """
        exceptions = []
        for c in self.clauses:
            try:
                # try with fake context
                c._check_contract(context.copy(), value, silent=False)
                # if ok, do with main context
                c._check_contract(context, value, silent=False)

                assert False, "We should not be here."
            except ContractNotRespected as e:
                exceptions.append((c, e))
        else:
            msg = self._format_exceptions(exceptions)
            raise ContractNotRespected(contract=self, error=msg,
                        value=value, context=context)

    def _format_exceptions(self, exceptions):
        msg = ('Could not satisfy any of the %d clauses in %s.'
               % (len(self.clauses), self))

        for i, ex in enumerate(exceptions):
            c, e = ex
            if i + 1 > 1:
                msg += '\n ├┄┄┄ Clause #%d:   %s\n' % (i + 1, c)
            else:
                msg += '\n ┬┄┄┄┄ Clause #%d:   %s\n' % (i + 1, c)
            msg += add_prefix('%s' % e, ' | ')

        msg += '\n ╰┄┄┄┄┄┄ (end clauses) ┄┄┄┄┄┄'
        return msg

    def __repr__(self):
        s = 'OR(%r)' % self.clauses
        return s

    @staticmethod
    def parse_action(string, location, tokens):
        l = list(tokens[0])
        clauses = [l.pop(0)]
        while l:
            glyph = l.pop(0)  # @UnusedVariable
            assert glyph == OR_GLYPH
            operand = l.pop(0)
            clauses.append(operand)
        where = W(string, location)
        return OR(clauses, where=where)


class And(Logical, Contract):
    def __init__(self, clauses, where=None):
        assert isinstance(clauses, list)
        assert len(clauses) >= 2, clauses
        Contract.__init__(self, where)
        Logical.__init__(self, AND_GLYPH, 2)
        self.clauses = clauses

    def check_contract(self, context, value, silent):
        for c in self.clauses:
            c._check_contract(context, value, silent)

    def __repr__(self):
        s = 'And(%r)' % self.clauses
        return s

    @staticmethod
    def parse_action(string, location, tokens):
        l = list(tokens[0])
        clauses = [l.pop(0)]
        while l:
            glyph = l.pop(0)  # @UnusedVariable
            assert glyph == AND_GLYPH
            operand = l.pop(0)
            clauses.append(operand)
        where = W(string, location)
        return And(clauses, where=where)


class Not(Logical, Contract):
    def __init__(self, clauses, where=None):
        assert isinstance(clauses, list)
        assert len(clauses) == 1, clauses
        Contract.__init__(self, where)
        Logical.__init__(self, NOT_GLYPH, 3)
        self.clauses = clauses

    def check_contract(self, context, value, silent):
        clause = self.clauses[0]
        try:
            clause._check_contract(context, value, silent)
        except ContractNotRespected:
            pass
        else:
            msg = "Shouldn't have satisfied the clause %s." % clause
            raise ContractNotRespected(contract=self, error=msg,
                                       value=value, context=context)

    @staticmethod
    def parse_action(string, location, tokens):
        l = list(tokens[0])
        assert l.pop(0) == NOT_GLYPH
        where = W(string, location)
        return Not(l, where=where)

    def __repr__(self):
        s = 'Not(%r)' % self.clauses
        return s

    def __str__(self):
        return self.glyph + self._convert(self.clauses[0])


suggester = create_suggester(get_options=lambda: ParsingTmp.keywords +
                             list(Extension.registrar.keys()))
baseExpr = simple_contract | suggester
baseExpr.setName('Simple contract (recovering)')


op = myOperatorPrecedence
# op = operatorPrecedence
composite_contract = op(baseExpr, [
                         (NOT_GLYPH, 1, opAssoc.RIGHT, Not.parse_action),
                         (AND_GLYPH, 2, opAssoc.LEFT, And.parse_action),
                         (OR_GLYPH, 2, opAssoc.LEFT, OR.parse_action),
                    ])
composite_contract.setName('NOT/OR/AND contract')

or_contract = op(baseExpr, [
                         (OR_GLYPH, 2, opAssoc.LEFT, OR.parse_action),
                    ])
or_contract.setName('OR contract')
