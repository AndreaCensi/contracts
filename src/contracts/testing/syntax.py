from pyparsing import delimitedList, Forward

contract = Forward()

contract << delimitedList(contract)  

number = 0

list_options = 
                O(number)
list_contract = Literal('list') + \
                O(Literal('(')  O(number) + Literal(')'))


contract << 'list'
