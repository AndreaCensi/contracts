from contracts import parse, ContractSyntaxError
from contracts.library.tuple import tuple_contract

from contracts.interface import Where
from contracts.syntax import rvalue, ParseFatalException, ParseException
from contracts.library.lists import     list_contract

# 
# try:
#     parse('a,b,(c|?),d')
#     
# except ContractSyntaxError as e:
#     print e

def parser(expression):
    def f(string):
        try:
            expression.parseString(string, parseAll=True)
        except ParseException as e:
            where = Where(string, line=e.lineno, column=e.col)
            msg = 'Error in parsing string: %s' % e
            raise ContractSyntaxError(msg, where=where)
        except ParseFatalException as e:
            where = Where(string, line=e.lineno, column=e.col)
            msg = 'Fatal error in parsing string: %s' % e
        raise ContractSyntaxError(msg, where=where)    
    return f

def tryparser(parser, string):
    try:
        parser(string)
    except ContractSyntaxError as e:
        print e
    
rvalue_parser = parser(rvalue)
list_parser = parser(list_contract)
tuple_parser = parser(tuple_contract)



# tryparser(tuple_parser, 'tuple(str,a,?)')# 
# tryparser(tuple_parser, 'tuple(str,a,?,b,c)')
#tryparser(parse, 'list(1,2,(tuple(str,a,(?)))')
print('===========================')
tryparser(parse, 'tuple(?)')
# tryparser(tuple_parser, 'tuple(?)') # Expected: unnamed (instance of Or) (at char 6), (line:1, col:7)

tryparser(parse, 'list(?)')
# tryparser(list_parser, 'list(?)')
tryparser(parse, 'list(1,?)')
# tryparser(list_parser, 'list(1,2,(tuple(str,a,(?)))')
tryparser(parse, 'list(1,2,(tuple(str,a,(?)))')
tryparser(parse, 'list(1,2,(,tuple(str,a,(?)))')

tryparser(parse, '1+2+3+(4+(3*2?))+3')
# tryparser(rvalue_parser, '1+(3*2?)')
tryparser(parse, '1+(3*2?)')
    
    

    # 
    # 
    # try:
    #     parse('list(int,str*)')
    #     
    # except ContractSyntaxError as e:
    #     print e
    # 
    # 
    # try:
    #     parse('tuple(int,a,str*)')
    #     
    # except ContractSyntaxError as e:
    #     print e
    #     
    # try:
    #     parse('list[N](>0,tuple(int,str*))')
    # 
    # except ContractSyntaxError as e:
    #     print e