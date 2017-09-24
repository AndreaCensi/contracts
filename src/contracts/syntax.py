from numbers import Number
import math


# All the imports from pyparsing go here
from pyparsing import (delimitedList, Forward, Literal,
                       stringEnd, nums, Word, CaselessLiteral, Combine,
                       Optional, Suppress, OneOrMore, ZeroOrMore, opAssoc,
                       operatorPrecedence, oneOf, ParseException,
                       ParserElement,
                       alphas, alphanums, ParseFatalException,
                       ParseSyntaxException, FollowedBy, NotAny, Or,
                       MatchFirst, Keyword, Group, White, lineno, col)


# from .pyparsing_utils import myOperatorPrecedence


# Enable memoization (much faster!)
if True:
    ParserElement.enablePackrat()
else:
    # Pyparsing 2.0
    from pyparsing import infixNotation
    myOperatorPrecendence = infixNotation

from .interface import Where


class ParsingTmp():
    # TODO: FIXME: decide on an order, if we do the opposite it doesn't work.
    contract_types = []
    keywords = []


def add_contract(x):
    ParsingTmp.contract_types.append(x)


def add_keyword(x):
    """ Declares that x is a keyword --- this is useful to have more
        clear messages. "keywords" are not parsed by Extension.
        (see extensions.py) and allows to have "deep" error indications.
        See http://pyparsing.wikispaces.com/message/view/home/620225
        and the discussion of the "-" operator in the docs.
    """
    ParsingTmp.keywords.append(x)

W = Where


O = Optional
S = Suppress

basenumber = Word(nums)
point = Literal('.')
e = CaselessLiteral('E')
plusorminus = Literal('+') | Literal('-')
integer = Combine(O(plusorminus) + basenumber)
integer.setParseAction(lambda tokens: SimpleRValue(int(tokens[0])))
floatnumber = Combine(
    O(plusorminus) + integer + (point + O(basenumber)) ^ (e + integer))
floatnumber.setParseAction(lambda tokens: SimpleRValue(float(tokens[0])))
pi = Keyword('pi').setParseAction(
    lambda tokens: SimpleRValue(math.pi, 'pi'))  # @UnusedVariable


try:
    import numpy
except ImportError:
    numpy = None

def isnumber(x):
    # These are scalar quantities that we can compare (=,>,>=, etc.)
    if isinstance(x, Number):
        return True

    if numpy is not None and isinstance(x, numpy.number):
        return True

    return False

rvalue = Forward()
rvalue.setName('rvalue')
contract_expression = Forward()
contract_expression.setName('contract')
simple_contract = Forward()
simple_contract.setName('simple_contract')

# Import all expressions -- they will call add_contract()
from .library import (EqualTo, Unary, Binary, composite_contract,
                      identifier_contract, misc_variables_contract,
                      scoped_variables_ref,
                      int_variables_contract, int_variables_ref,
                      misc_variables_ref, SimpleRValue)


number = pi | floatnumber | integer
operand = number | int_variables_ref | misc_variables_ref | scoped_variables_ref
operand.setName('r-value')


op = operatorPrecedence
# op  = myOperatorPrecedence
rvalue << op(operand, [
    ('-', 1, opAssoc.RIGHT, Unary.parse_action),
    ('*', 2, opAssoc.LEFT, Binary.parse_action),
    ('-', 2, opAssoc.LEFT, Binary.parse_action),
    ('+', 2, opAssoc.LEFT, Binary.parse_action),
    ('^', 2, opAssoc.LEFT, Binary.parse_action),
])


# I want
# - BindVariable to have precedence to EqualTo(VariableRef)
# but I also want:
# - Arithmetic to have precedence w.r.t BindVariable
# last is variables
add_contract(misc_variables_contract)
add_contract(int_variables_contract)

add_contract(rvalue.copy().setParseAction(EqualTo.parse_action))

hardwired = MatchFirst(ParsingTmp.contract_types)
hardwired.setName('Predefined contract expression')

simple_contract << (hardwired | identifier_contract)
simple_contract.setName('simple contract expression')

any_contract = composite_contract | simple_contract
any_contract.setName('Any simple or composite contract')
contract_expression << (any_contract)  # Parentheses before << !!
