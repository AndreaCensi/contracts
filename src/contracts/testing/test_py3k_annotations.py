import sys

inPy3k = sys.version_info[0] == 3

if inPy3k:
    import unittest
    from contracts import decorate, ContractException, contracts, ContractNotRespected
    
    class Py3kAnnotationsTest(unittest.TestCase):
    
        def test_malformed(self):
            def f() -> "":
                pass
        
            self.assertRaises(ContractException, decorate, f)
    
        def test_malformed2(self):
            def f() -> "okok":
                pass
        
            self.assertRaises(ContractException, decorate, f)
    
        def test_malformed3(self):
            def f() -> 3:
                pass
        
            self.assertRaises(ContractException, decorate, f)
        
        def test_not_specified1(self):
            ''' No docstring specified, but annotation is. '''
            def f() -> "int":
                pass
        
        def test_parse_error1(self):
            def f(a: "int", b: "in"):
                pass
        
            self.assertRaises(ContractException, decorate, f)

        def test_parse_error2(self):
            def f(a, b) -> "in":
                pass
            self.assertRaises(ContractException, decorate, f)


        def not_supported2(self):
            ''' Cannot do with **args ''' 
            def f(a, **b):
                ''' 
                    :type a: int
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

        def test_types1(self):
            @contracts
            def f(a: int, b: int) -> int:
                return a + b 

            f(1, 2)
            self.assertRaises(ContractNotRespected, f, 1.0, 2)
            self.assertRaises(ContractNotRespected, f, 1, 2.0)

        def test_types2(self):
            ''' Testing return value contract '''
            @contracts
            def f(a: int, b: int) -> int:
                return (a + b)  * 2.1

            self.assertRaises(ContractNotRespected, f, 1, 2)
    

        def test_kwargs(self):
            def f(a:int, b:int, c:int=7): #@UnusedVariable
                if c != b:
                    raise Exception()

        
            f2 = decorate(f)
            f2(0, 7)
            f2(0, 5, 5)
            self.assertRaises(Exception, f2, 0, 5, 4)
            self.assertRaises(Exception, f2, 0, 5)

        def test_varargs(self):
            def f(a, b, *c: tuple):
                assert c == (a, b)
        
            f2 = decorate(f)
            f2(0, 7, 0, 7)

        def test_varargs2(self):
            def f(a, b, *c: "tuple"):
                assert c == (a, b)
        
            f2 = decorate(f)
            f2(0, 7, 0, 7)

        def test_keywords(self):
            def f(A:int, B:int, **c: dict):
                assert c['a'] == A
                assert c['b'] == B
                    
            f2 = decorate(f)
            f(0, 7, a=0, b=7)
            f2(0, 7, a=0, b=7)
        
            self.assertRaises(Exception, f2, 0, 5, 0, 6)
            
            