#cython: language_level=3, annotation_typing=True, c_string_encoding=utf-8, boundscheck=False, wraparound=False, initializedcheck=False
from functools import reduce

from Aspidites._vendor._compat import basestring

from ..interface import RValue
from ..syntax import isnumber, W


class Binary(RValue):
    operations = {
        '+': lambda x, y: x + y,
        '-': lambda x, y: x - y,
        '*': lambda x, y: x * y,
        '^': lambda x, y: x ** y,
    }

    precedence = {
        '+': 0,
        '-': 0,
        '*': 1,
        '^': 2,
    }

    def __init__(self, exprs, glyph, where=None):
        assert glyph in  Binary.operations
        for e in exprs:
            assert isinstance(e, RValue)

        self.where = where
        self.exprs = exprs
        self.glyph = glyph
        self.precedence = Binary.precedence[glyph]

    def eval(self, context):  # @ReservedAssignment
        vals = []
        for expr in self.exprs:
            val = expr.eval(context)
            if not isnumber(val):
                raise ValueError('I can only do math with numbers, not %r.' %
                                 val.__class__.__name__)
            vals.append(val)
        operation = Binary.operations[self.glyph]
        return reduce(operation, vals)

    def __repr__(self):
        s = 'Binary(%r,%r)' % (self.exprs, self.glyph)
        return s

    def __str__(self):
        def convert(x):
            if isinstance(x, Binary) and x.precedence < self.precedence:
                return '(%s)' % x
            else:
                return '%s' % x

        s = self.glyph.join(convert(x) for x in self.exprs)
        return s

    @staticmethod
    def parse_action(s, loc, tokens):
        where = W(s, loc)
        l = list(tokens[0])
        exprs = [l.pop(0)]
        while l:
            glyph = l.pop(0)
            assert isinstance(glyph, basestring)
            expr = l.pop(0)
            assert isinstance(expr, RValue)
            exprs.append(expr)

        # noinspection PyUnboundLocalVariable
        return Binary(exprs, glyph, where=where)


class Unary(RValue):

    operations = {
        '-': lambda x: (-x),
    }

    def __init__(self, glyph, expr, where=None):
        assert glyph in Unary.operations
        assert isinstance(expr, RValue)

        self.where = where
        self.expr = expr
        self.glyph = glyph

    def eval(self, context):  # @ReservedAssignment
        val = self.expr.eval(context)
        if not isnumber(val):
            raise ValueError('I can only do math with numbers, not with %r.' %
                   val.__class__.__name__)

        operation = Unary.operations[self.glyph]
        return operation(val)

    def __repr__(self):
        s = 'Unary(%r,%r)' % (self.glyph, self.expr)
        return s

    def __str__(self):
        # XXX: precedence
        return '%s%s' % (self.glyph, self.expr)

    @staticmethod
    def parse_action(s, loc, tokens):
        where = W(s, loc)
        glyph = tokens[0][0]
        assert isinstance(glyph, basestring)
        expr = tokens[0][1]
        assert isinstance(expr, RValue)
        return Unary(glyph, expr, where=where)

