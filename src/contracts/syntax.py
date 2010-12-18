from pyparsing import ParserElement
from contracts.interface import Contract, ContractNotRespected
ParserElement.enablePackrat()

from pyparsing import (delimitedList, Forward, Literal, stringEnd, nums, Word, #@UnusedImport
    CaselessLiteral, Combine, Optional, Suppress, OneOrMore, ZeroOrMore, opAssoc, #@UnusedImport
    operatorPrecedence)
from procgraph.core.parsing_elements import Where 
import numbers

class ParsingTmp:
    current_filename = 'unknown' 
    contract_types = []
    rvalues_types = []

def W(string, location):
    return Where(ParsingTmp.current_filename, string, location)

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
    ParsingTmp.rvalues_types.append(x)

from . import library #@UnusedImport
from library.compositions import composite_contract



from contracts.library.arithmetic import Unary, Binary

operand = (integer | floatnumber) | get_or(ParsingTmp.rvalues_types)

expr = operatorPrecedence(operand,
    [
     ('-', 1, opAssoc.RIGHT, Unary.parse_action),
     ('*', 2, opAssoc.LEFT, Binary.parse_action),
     ('-', 2, opAssoc.LEFT, Binary.parse_action),
     ('+', 2, opAssoc.LEFT, Binary.parse_action),
    ]
    
    )

rvalue << expr 


class EqualTo(Contract):
    def __init__(self, rvalue, where=None):
        Contract.__init__(self, where)
        self.rvalue = rvalue
        
    def check_contract(self, context, value):
        val = context.eval(self.rvalue, self)
        if not(val == value):
            error = ('Condition %s == %s not respected.' % (val, value))
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

add_contract(rvalue.copy().setParseAction(EqualTo.parse_action))

simple_contract << get_xor(ParsingTmp.contract_types)

contract << ((composite_contract | simple_contract)) # Parentheses before << !!

