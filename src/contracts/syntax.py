from pyparsing import ParserElement
ParserElement.enablePackrat()

from pyparsing import delimitedList, Forward, Literal, stringEnd, nums, Word, \
    CaselessLiteral, Combine, Optional, Suppress, OneOrMore, ZeroOrMore, opAssoc, \
    operatorPrecedence
from procgraph.core.parsing_elements import Where 
import numbers

class ParsingTmp:
    current_filename = 'unknown' 
    contract_types = []
    rvalues_types = []

def W(string, location):
    return Where(ParsingTmp.current_filename, string, location)

O = Optional
S = Suppress

number = Word(nums) 
point = Literal('.')
e = CaselessLiteral('E')
plusorminus = Literal('+') | Literal('-')
integer = Combine(O(plusorminus) + number)
floatnumber = Combine(integer + O(point + O(number)) + O(e + integer))
integer.setParseAction(lambda tokens: int(tokens[0]))
floatnumber.setParseAction(lambda tokens: float(tokens[0]))

isnumber = lambda x: isinstance(x, numbers.Number)

rvalue = Forward()
contract = Forward()
simple_contract = Forward()

def add_contract(x):
    ParsingTmp.contract_types.append(x)
def add_rvalue(x): 
    #print 'Adding', x
    ParsingTmp.rvalues_types.append(x)

from . import library #@UnusedImport
from library.compositions import composite_contract


# Finally define the simple contract
def get_xor(l):
    tmp = l[0]
    for i in range(1, len(l)):
        tmp = tmp.__xor__(l[i])
    return tmp
def get_or(l):
    tmp = l[0]
    for i in range(1, len(l)):
        tmp = tmp.__or__(l[i])
    return tmp


from contracts.library.arithmetic import parse_arithmetic_rvalue, \
    parse_unary_minus

operand = (floatnumber | integer) | get_or(ParsingTmp.rvalues_types)

expr = operatorPrecedence(operand,
    [
     ('-', 1, opAssoc.RIGHT, parse_unary_minus),
     ('*', 2, opAssoc.LEFT, parse_arithmetic_rvalue(lambda x, y:x * y, '*')),
     ('-', 2, opAssoc.LEFT, parse_arithmetic_rvalue(lambda x, y:x - y, '-')),
     ('+', 2, opAssoc.LEFT, parse_arithmetic_rvalue(lambda x, y:x + y, '+')),
    ]
    
    )

rvalue << expr 

from contracts.library.comparison import CheckOrder

def parse_as_contract(s, loc, tokens):
    where = W(s, loc)
    rvalue = tokens[0]
    return CheckOrder(where, None, rvalue, False, True, False)

add_contract(rvalue.copy().setParseAction(parse_as_contract))

simple_contract << get_xor(ParsingTmp.contract_types)

contract << ((composite_contract | simple_contract)) # Parentheses before << !!

