import unittest

from contracts import new_contract, check, ContractSyntaxError
from contracts.interface import ContractNotRespected

# The different patterns

def ok1(x):
    pass

def ok2(x):
    return True

def fail1(x):
    raise ValueError('message')

def fail2(x):
    return False

def invalid_callable1(x):
    return 'ciao'
    
class TestNewContract(unittest.TestCase):
    
    def test_inverted_args(self):
        self.assertRaises(ValueError, new_contract, ok1, 'list')
    
    def test_invalid_callable(self):
        self.assertRaises(ValueError, new_contract, 'new', lambda:None)
        
    def test_parsing_error(self):
        self.assertRaises(ContractSyntaxError, new_contract, 'new', '>>')

    def test_parsing_error2(self):
        # parsing error (unknown spec)
        self.assertRaises(ContractSyntaxError, new_contract, 'new', 'unknown')
        
    def test_invalid_names(self):
        # invalid names:
        alphabet = 'A B C D E F G H I J K L M N O P Q R S T U W V X Y Z'
        for x in alphabet.split():
            self.assertRaises(ValueError, new_contract, x, 'list')
            self.assertRaises(ValueError, new_contract, x.lower(), 'list')
        self.assertRaises(ValueError, new_contract, 'list', 'list[N]')
        
    def test_valid(self):
        new_contract('my_list', 'list[2]')
        check('tuple(my_list, my_list)', ([1, 2], [1, 2]))
        self.assertRaises(check, 'tuple(my_list, my_list)', ([1, 2], [1, 2, 3]))
    
    def test_separate_context(self):
        new_contract('my_list2', 'list[N]')
        check('tuple(my_list2, my_list2)', ([1, 2], [1, 2]))
        check('tuple(my_list2, my_list2)', ([1, 2], [1, 2, 3]))

    def test_renaming(self):
        new_contract('my7', ok1)
        self.assertRaises(ValueError, new_contract, 'my7', ok2)
    
    def test_allow_renaming_if_equal1(self):
        new_contract('my8', ok1)
        new_contract('my8', ok1)

    def test_allow_renaming_if_equal2(self):
        new_contract('my8', 'list[3]')
        new_contract('my8', 'list[3]')
        
    def test_callable1(self):
        new_contract('my3', ok1)
        check('list(my3)', [0])
        
    def test_callable2(self):
        new_contract('my4', ok2)
        check('list(my4)', [0])
    
    def test_callable3(self):
        new_contract('my5', fail1)
        self.assertRaises(ContractNotRespected, check, 'list(my5)', [0])
        
    def test_callable4(self):
        new_contract('my9', fail2)
        self.assertRaises(ContractNotRespected, check, 'list(my9)', [0])
        
    def test_invalid_callable2(self):
        new_contract('my10', invalid_callable1)
        self.assertRaises(ValueError, check, 'list(my10)', [0])
            
    def test_other_pass(self):
        class Ex1:
            pass
        def invalid(x):
            raise Ex1()
        new_contract('my11', invalid)
        self.assertRaises(Ex1, check, 'list(my11)', [0])
        
         
