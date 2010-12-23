import unittest

from contracts import decorate, contracts
from ..interface import ContractException, ContractNotRespected

class DecoratorTests(unittest.TestCase):
    
    
    def test_malformed(self):
        def f():
            ''' 
                Wrong syntax 
            
                :rtype okok
            '''
            pass
        
        self.assertRaises(ContractException, decorate, f)
    
    def test_malformed2(self):
        def f():
            ''' 
                Wrong syntax 
            
                :rtype: okok
            '''
            pass
        
        self.assertRaises(ContractException, decorate, f)
    
        
    def test_not_specified1(self):
        ''' No docstring specified '''
        def f():
            pass
        
        self.assertRaises(ContractException, decorate, f)

    def test_not_specified2(self):
        def f():
            ''' No types specified in the docstring '''
            pass
        
        self.assertRaises(ContractException, decorate, f)


    def test_too_many(self):
        def f():
            ''' 
                Too many rtype clauses.
                :rtype: int
                :rtype: int
            '''
            pass
        
        self.assertRaises(ContractException, decorate, f)

    def test_invalid1(self):
        def f(a):
            ''' Unknown b.
                :type a: int
                :type b: int
            '''
            pass
        
        self.assertRaises(ContractException, decorate, f)

    def test_parse_error1(self):
        def f(a, b):
            ''' Same with optional
                :type a: in
                :type b: int
            '''
            pass
        
        self.assertRaises(ContractException, decorate, f)

    def test_parse_error2(self):
        def f(a, b):
            ''' Same with optional
                :type a: int
                :type b: int
                :rtype: in
            '''
            pass
        
        self.assertRaises(ContractException, decorate, f)

    def not_supported1(self):
        ''' Support of *args ''' 
        def f(a, *b):
            ''' 
                :type a: int
                :type b: tuple(int)
                :rtype: int
            '''
            pass
        
            decorate(f)

    def not_supported2(self):
        ''' Support of **args ''' 
        def f(a, **b):
            ''' 
                :type a: int
                :type b: dict(int:int)
                :rtype: int
            '''
            pass
        
        self.assertRaises(ContractException, decorate, f)


    def test_ok1(self):
        @contracts
        def f(a, b):
            ''' This is good
                :type a: int
                :type b: int
                :rtype: int
            '''
            pass

    def test_ok3(self):
        ''' Trying the quoting thing. '''
        @contracts
        def f(a, b):
            ''' This is good
                :type a: ``int``
                :type b: ``int``
                :rtype: ``int``
            '''
            pass

    def test_bad_quoting(self):
        def f(a, b):
            ''' 
                :type a: ``int``
                :type b: ``int``
                :rtype: ``int`
            '''
            pass

        self.assertRaises(ContractException, decorate, f)

    def test_bad_quoting2(self):
        def f(a, b):
            ''' 
                :type a: ``int``
                :type b: `int``
                :rtype: ``int``
            '''
            pass

        self.assertRaises(ContractException, decorate, f)

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

    # def test_module_as_decorator(self):
    #     import contracts as contract_module
    # 
    #     @contract_module
    #     def f(a, b): #@UnusedVariable
    #         return a + b
    #     f(1, 2)
    #     self.assertRaises(ContractNotRespected, f, 1.0, 2)
        
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
        
        f2 = decorate(f)
        self.assertEqual(f.__doc__, f2.__doc__)
    

    def test_kwargs(self):
        def f(a, b, c=7): #@UnusedVariable
            ''' Same with optional
                :type a: int
                :type b: int
                :type c: int
            '''
            if c != b:
                raise Exception()

        
        f2 = decorate(f)
        f2(0, 7)
        f2(0, 5, 5)
        self.assertRaises(Exception, f2, 0, 5, 4)
        self.assertRaises(Exception, f2, 0, 5)

    def test_varargs(self):
        def f(a, b, *c):
            ''' Same with optional
                :type a: int
                :type b: int
                :type c: tuple
            '''
            assert c == (a, b)

        
        f2 = decorate(f)
        f2(0, 7, 0, 7)

    def test_keywords(self):
        def f(A, B, **c):
            ''' Same with optional
                :type A: int
                :type B: int
                :type c: dict
            '''
            assert c['a'] == A
            assert c['b'] == B
            
        
        f2 = decorate(f)
        f(0, 7, a=0, b=7)
        f2(0, 7, a=0, b=7)
        
        self.assertRaises(Exception, f2, 0, 5, 0, 6)
        

