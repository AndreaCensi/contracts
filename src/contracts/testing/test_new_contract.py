import unittest

from contracts import new_contract, check, ContractSyntaxError, ContractNotRespected
from contracts.library.extensions import identifier_expression
from contracts.interface import Contract
from contracts.testing.utils import check_contracts_fail
from contracts.main import contracts

# The different patterns

def ok1(x):
    pass

def ok2(x): #@UnusedVariable
    return True

def fail1(x):
    raise ValueError('message')

def fail2(x): #@UnusedVariable
    return False

def invalid_callable1(x): #@UnusedVariable
    return 'ciao'
    
if 1:
    class TestNewContract(unittest.TestCase):
        
        def test_inverted_args(self):
            self.assertRaises(ValueError, new_contract, ok1, 'list')
        
        def test_wrong_args(self):
            self.assertRaises(ValueError, new_contract, 'my13', 2)
        
        def test_invalid_callable(self):
            self.assertRaises(ValueError, new_contract, 'new', lambda:None)
            
        def test_parsing_error(self):
            self.assertRaises(ValueError, new_contract, 'new', '>>')
    
        def test_parsing_error2(self):
            # parsing error (unknown spec)
            self.assertRaises(ValueError, new_contract, 'new', 'unknown')
            
        def test_invalid_names(self):
            # invalid names:
            alphabet = 'A B C D E F G H I J K L M N O P Q R S T U W V X Y Z'
            for x in alphabet.split():
                self.assertRaises(ValueError, new_contract, x, 'list')
                self.assertRaises(ValueError, new_contract, x.lower(), 'list')
            self.assertRaises(ValueError, new_contract, 'list', 'list[N]')
            self.assertRaises(ValueError, new_contract, '2acdca', 'list[N]')
            self.assertRaises(ValueError, new_contract, '_', 'list[N]')
        
        def test_valid_identifiers(self):
            examples = ['aa', 'a_', 'a2', 'a_2']
            
            def check_valid_identifier(e):
                c = identifier_expression.parseString(e, parseAll=True)
                assert isinstance(c, Contract)
                
            for e in examples:
                yield check_valid_identifier, e
                
        def test_valid(self):
            c = new_contract('my_list', 'list[2]')
            assert isinstance(c, Contract)
            check('tuple(my_list, my_list)', ([1, 2], [1, 2]))
            check_contracts_fail('tuple(my_list, my_list)', ([1, 2], [1, 2, 3]))
        
        def test_separate_context(self):
            new_contract('my_list2', 'list[N]')
            check('tuple(my_list2, my_list2)', ([1, 2], [1, 2]))
            check('tuple(my_list2, my_list2)', ([1, 2], [1, 2, 3]))
    
        def test_renaming(self):
            self.assertNotEqual(ok1, ok2)
            new_contract('my7', ok1)
            self.assertRaises(ValueError, new_contract, 'my7', ok2)
        
        def test_allow_renaming_if_equal1(self):
            new_contract('my8', ok1)
            new_contract('my8', ok1)
    
        def test_allow_renaming_if_equal2(self):
            new_contract('my8b', 'list[3]')
            new_contract('my8b', 'list[3]')
            
        def test_callable1(self):
            new_contract('my3', ok1)
            check('list(my3)', [0])
            
        def test_callable2(self):
            new_contract('my4', ok2)
            check('list(my4)', [0])
        
        def test_callable3(self):
            new_contract('my5', fail1)
            check_contracts_fail('list(my5)', [0])
            
        def test_callable4(self):
            new_contract('my9', fail2)
            check_contracts_fail('list(my9)', [0])
            
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
    
        def test_callable(self):
            class MyTest_ok(object):
                def __call__(self, x): #@UnusedVariable
                    return True
            o = MyTest_ok()
            assert o('value') == True
            new_contract('my15a', o)
        
        def test_callable_5(self):
            class MyTest_ok(object):
                def f(self, x): #@UnusedVariable
                    return True
            o = MyTest_ok()
            assert o.f('value') == True
            new_contract('my15b', o.f)
        
        def test_callable_invalid(self):
            class MyTest_fail(object):
                def __call__(self, x, y): #@UnusedVariable
                    return True
                
            self.assertRaises(ValueError, new_contract, 'my16', MyTest_fail())
            
        def test_lambda_2(self):
            new_contract('my17', lambda x: True) #@UnusedVariable
            new_contract('my17b', lambda x: None) #@UnusedVariable
        
        def test_lambda_invalid(self):
            f = lambda x, y: True #@UnusedVariable
            self.assertRaises(ValueError, new_contract, 'my18', f)
        
        def test_lambda_invalid2(self):
            self.assertRaises(ValueError, new_contract, 'my18', lambda: True)

        def test_idioms(self):
            color = new_contract('color', 'list[3](number,>=0,<=1)')
            # Make sure we got it right
            color.check([0, 0, 0])
            color.check([0, 0, 1])
            color.fail([0, 0])
            color.fail([0, 0, 2])
            
            self.assertRaises(ValueError, color.fail, [0, 0, 1])
            
            # Now use ``color`` in other contracts.
            @contracts
            def fill_area(inside, border):
                """ Fill the area inside the current figure.
                
                    :type border: color
                    :type inside: color
                """
                pass
                
            @contracts
            def fill_gradient(colors):
                """ Use a gradient to fill the area.
                
                    :type colors: list(color)
                """
                pass
