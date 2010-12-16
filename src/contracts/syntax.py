from pyparsing import delimitedList, Forward, Literal, stringEnd, nums, Word, \
    CaselessLiteral, Combine, Optional, Suppress, OneOrMore
from procgraph.core.parsing_elements import Where 


class ParsingTmp:
    current_filename = 'unknown' 
    contract_types = []

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

rvalues = (integer | floatnumber) 


contract = Forward()
simple_contract = Forward()

def add_contract(x):
    ParsingTmp.contract_types.append(x)


from . import library #@UnusedImport
from library.compositions import composite_contract


# Finally define the simple contract
def get_definition_simple_contract():
    l = ParsingTmp.contract_types 
    tmp = l[0]
    for i in range(1, len(l)):
        tmp = tmp.__xor__(l[i])
    return tmp

simple_contract << get_definition_simple_contract()

contract << ((composite_contract | simple_contract)) # Parentheses before << !!

