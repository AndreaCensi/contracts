from ..interface import ExternalScopedVariableNotFound
from ..syntax import S, W
from ..utils import ignore_typeerror
from pyparsing import Word, alphanums
import inspect
from contracts.library.types_misc import CheckType


def _lookup_from_calling_scope(token):
    """
    Extract the value of the token from the scope where the spec is defined
    """

    # We walk the callstack from the outside in, searching for the
    # frame where the spec is defined
    #
    # XXX Check if there are other places where a spec might be defined
    from .. import decorate, parse, check, fail

    def _code(f):
        try:  # py2
            return f.func_code
        except AttributeError:  # py3
            return f.__code__

    frames = inspect.getouterframes(inspect.currentframe())
    frames = [f[0] for f in frames[::-1]]
    fcodes = [f.f_code for f in frames]

    def find_invokation(func):
        # return the first frame where func is called, or raise ValueError
        # find first frame inside function, step out 1
        return lambda: frames[fcodes.index(_code(func)) - 1]

    def find_decorate():
        # return the first frame where decorate is called, or raise ValueError

        # Brittle: We must to determine whether user calls decorate
        #          directly (in which case relevant scope is 1 frame out)
        #          or indirectly via @contract() (scope is 2 frames out)
        #          The implementation relies on the name `tmp_wrap` of the
        #          hidden function inside @contract.
        idx = fcodes.index(_code(decorate))

        if frames[idx - 1].f_code.co_name == 'tmp_wrap':
            # decorate() called via @contract, Step out 2 frames
            return frames[idx - 2]

        # decorate() called oustide of @contract, step out 1 frame
        return frames[idx - 1]

    # search order important
    searchers = [find_decorate,
                 find_invokation(check),
                 find_invokation(fail),
                 find_invokation(parse)]
    for s in searchers:
        try:
            f = s()
        except (ValueError, IndexError):
            continue
        if not f:
            continue
        try:
            return eval(token, f.f_locals, f.f_globals)
        except NameError:
            raise ExternalScopedVariableNotFound(token)

    raise RuntimeError("Cound not find a scope to lookup %s" % token)


# class ScopedVariableRef(RValue):
#
#     """
#     A variable whose value is extracted by name from the scope where the spec is defined.
#     """
#
#     def __init__(self, value, where=None):
#         self.where = where
#         self.value = value
#
#     def eval(self, context):
#         return self.value
#
#     def __repr__(self):
#         return "ScopedVariableRef(%r)" % self.value
#
#     def __str__(self):
#         return str(self.value)

@ignore_typeerror
def scoped_parse_action(s, loc, tokens):
    assert len(tokens) == 1
    where = W(s, loc)
    val = _lookup_from_calling_scope(tokens[0])

    from contracts.library.simple_values import SimpleRValue

    from contracts.inspection import can_be_used_as_a_type

    if can_be_used_as_a_type(val):
        return CheckType(val)
    else:
        return SimpleRValue(value=val, where=where, representation=s)

scoped_variables = (S('$') + Word(alphanums + '_'))
scoped_variables_ref = scoped_variables.setParseAction(scoped_parse_action)





