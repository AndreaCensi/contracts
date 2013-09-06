from abc import abstractmethod
from contracts import ContractNotRespected, contract, ContractsMeta
import unittest
from contracts import CannotDecorateClassmethods
import functools
import nose


def expected_failure(test):
    @functools.wraps(test)
    def inner(*args, **kwargs):
        try:
            test(*args, **kwargs)
        except Exception:
            raise nose.SkipTest
        else:
            raise AssertionError('Failure expected')
    return inner


class TestMeta(unittest.TestCase):

    def test_meta_still_works1(self):
        
        class A():
            __metaclass__ = ContractsMeta
            
            @abstractmethod
            @contract(a='>0')
            def f(self, a):
                pass
        
        class B(A):
            # does not implement f
            pass
        
        self.assertRaises(TypeError, B)
        
    def test_meta_still_works2(self):
        
        class A():
            __metaclass__ = ContractsMeta
            
            # inverse order
            @contract(a='>0')
            @abstractmethod
            def f(self, a):
                pass
        
        class B(A):
            # does not implement f
            pass
            
        
        self.assertRaises(TypeError, B)
        
    def test_meta1(self):
        
        class A():
            __metaclass__ = ContractsMeta
            
            @abstractmethod
            @contract(a='>0')
            def f(self, a):
                pass
            
            
            @contract(a='>0')
            @abstractmethod
            def g(self, a):
                pass
            
        class B(A):
            
            def f(self, a):
                pass
            
            def g(self, a):
                pass
        
        b = B()
  
        self.assertRaises(ContractNotRespected, b.f, 0)
        self.assertRaises(ContractNotRespected, b.g, 0)

    @expected_failure
    def test_static1(self):
        
        class A():
            __metaclass__ = ContractsMeta
            
            @staticmethod
            @contract(a='>0')
            def f(a):
                pass
            
        self.assertRaises(ContractNotRespected, A.f, 0)
        
        class B(A):
            
            @staticmethod
            def f(a):
                pass
  
        self.assertRaises(ContractNotRespected, B.f, 0) # this doesn't work  
        
    @expected_failure   
    def test_classmethod1(self):
        
        class A():
            __metaclass__ = ContractsMeta
            
            @classmethod
            @contract(a='>0')
            def f(cls, a):  
                print('called A.f(%s)' % a)
                pass

        self.assertRaises(ContractNotRespected, A.f, 0)
            
        class B(A):
            
            @classmethod
            def f(cls, a):
                print('called B.f(%s)' % a)
                pass

        self.assertRaises(ContractNotRespected, B.f, 0) # this doesn't work  

    @expected_failure
    def test_classmethod1ns(self):
    
        class A(object):
            __metaclass__ = ContractsMeta
            
            @classmethod
            @contract(a='>0')
            def f(cls, a):
                print('called A.f(%s)' % a)
                pass

        self.assertRaises(ContractNotRespected, A.f, 0)
            
        class B(A):
            
            @classmethod
            def f(cls, a):
                print('called B.f(%s)' % a)
                pass

        self.assertRaises(ContractNotRespected, B.f, 0) # this doesn't work  
        

    def test_classmethod2a(self):
         
        def test_classmethod2():
            
            class A():
                __metaclass__ = ContractsMeta
                
                @contract(a='>0')
                @classmethod
                def f(cls, a):
                    pass
                
            class B(A):
                
                @classmethod
                def f(cls, a):
                    pass
      
        self.assertRaises(CannotDecorateClassmethods, test_classmethod2)
      
       

