import unittest

from ..main import contracts_decorate, contracts
from ..interface import ContractException, ContractNotRespected


class DecoratorTests(unittest.TestCase):
    
    
    def test_malformed(self):
        def f():
            ''' 
                Wrong syntax 
            
                :rtype okok
            '''
            pass
        
        self.assertRaises(ContractException, contracts_decorate, f)
    
    def test_malformed2(self):
        def f():
            ''' 
                Wrong syntax 
            
                :rtype: okok
            '''
            pass
        
        self.assertRaises(ContractException, contracts_decorate, f)
    
        
    def test_not_specified1(self):
        ''' No docstring specified '''
        def f():
            pass
        
        self.assertRaises(ContractException, contracts_decorate, f)

    def test_not_specified2(self):
        def f():
            ''' No types specified in the docstring '''
            pass
        
        self.assertRaises(ContractException, contracts_decorate, f)


    def test_too_many(self):
        def f():
            ''' 
                Too many rtype clauses.
                :rtype: int
                :rtype: int
            '''
            pass
        
        self.assertRaises(ContractException, contracts_decorate, f)

    def test_invalid1(self):
        def f(a):
            ''' Unknown b.
                :type a: int
                :type b: int
            '''
            pass
        
        self.assertRaises(ContractException, contracts_decorate, f)

    def test_not_enough1(self):
        def f(a, b, c):
            ''' No c?
                :type a: int
                :type b: int
            '''
            pass
        
        self.assertRaises(ContractException, contracts_decorate, f)

    def test_not_enough2(self):
        def f(a, b, c=True):
            ''' Same with optional
                :type a: int
                :type b: int
            '''
            pass
        
        self.assertRaises(ContractException, contracts_decorate, f)

    def test_parse_error1(self):
        def f(a, b):
            ''' Same with optional
                :type a: in
                :type b: int
            '''
            pass
        
        self.assertRaises(ContractException, contracts_decorate, f)

    def test_parse_error2(self):
        def f(a, b):
            ''' Same with optional
                :type a: int
                :type b: int
                :rtype: in
            '''
            pass
        
        self.assertRaises(ContractException, contracts_decorate, f)

    def not_supported1(self):
        ''' Cannot do with *args ''' 
        def f(a, *b):
            ''' 
                :type a: int
                :rtype: int
            '''
            pass
        
        self.assertRaises(ContractException, contracts_decorate, f)

    def not_supported2(self):
        ''' Cannot do with **args ''' 
        def f(a, **b):
            ''' 
                :type a: int
                :rtype: int
            '''
            pass
        
        self.assertRaises(ContractException, contracts_decorate, f)


    def test_ok1(self):
        @contracts
        def f(a, b):
            ''' This is good
                :type a: int
                :type b: int
                :rtype: int
            '''
            pass

    def test_ok2(self):
        @contracts(accepts=['int', 'int'], returns='int')
        def f(a, b):
            pass

    def test_check_it_works1(self):
        @contracts(accepts=['int', 'int'], returns='int')
        def f(a, b): #@UnusedVariable
            return 2.0
        self.assertRaises(ContractNotRespected, f, 1, 2)

    def test_check_it_works2(self):
        @contracts(accepts=['int', 'int'], returns='int')
        def f(a, b): #@UnusedVariable
            return a + b
        f(1, 2)
        self.assertRaises(ContractNotRespected, f, 1.0, 2)
        self.assertRaises(ContractNotRespected, f, 1, 2.0)

    def test_check_it_works3(self):
        @contracts
        def f(a, b):
            ''' This is good
                :type a: int
                :type b: int
                :rtype: int
            '''
            return a + b
        f(1, 2)
        self.assertRaises(ContractNotRespected, f, 1.0, 2)
        self.assertRaises(ContractNotRespected, f, 1, 2.0)
        
    def test_check_docstring_maintained(self):
        def f(a, b):
            ''' This is good
                :type a: int
                :type b: int
                :rtype: int
            '''
            return a + b
        
        f2 = contracts_decorate(f)
        self.assertEqual(f.__doc__, f2.__doc__)
    
