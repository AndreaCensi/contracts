import unittest

from contracts import (decorate, contract,
                ContractException, ContractNotRespected)

from contracts.interface import MissingContract


class DecoratorTests(unittest.TestCase):

    def test_malformed(self):
        def f():
            """
                Wrong syntax

                :rtype okok
            """
            pass

        self.assertRaises(ContractException, decorate, f)

    def test_malformed2(self):
        def f():
            """
                Wrong syntax

                :rtype: okok
            """
            pass

        self.assertRaises(ContractException, decorate, f)

    def test_not_specified1(self):
        """ No docstring specified """
        def f():
            pass

        self.assertRaises(ContractException, decorate, f)

    def test_not_specified2(self):
        def f():
            """ No types specified in the docstring """
            pass

        self.assertRaises(ContractException, decorate, f)

    def test_too_many(self):
        def f():
            """
                Too many rtype clauses.
                :rtype: int
                :rtype: int
            """
            pass

        self.assertRaises(ContractException, decorate, f)

    def test_invalid1(self):
        def f(a):
            """ Unknown b.
                :type a: int
                :type b: int
            """
            pass

        self.assertRaises(ContractException, decorate, f)

    def test_parse_error1(self):
        def f(a, b):
            """ Same with optional
                :type a: in
                :type b: int
            """
            pass

        self.assertRaises(ContractException, decorate, f)

    def test_parse_error2(self):
        def f(a, b):
            """ Same with optional
                :type a: int
                :type b: int
                :rtype: in
            """
            pass

        self.assertRaises(ContractException, decorate, f)

    def not_supported1(self):
        """ Support of *args """

        def f(a, *b):  # @UnusedVariable
            """
                :type a: int
                :type b: tuple(int)
                :rtype: int
            """
            pass

            decorate(f)

    def not_supported2(self):
        """ Support of **args """
        def f(a, **b):
            """
                :type a: int
                :type b: dict(int:int)
                :rtype: int
            """
            pass

        self.assertRaises(ContractException, decorate, f)

    def test_ok1(self):
        @contract
        def f(a, b):
            """ This is good
                :type a: int
                :type b: int
                :rtype: int
            """
            pass

    def test_ok3(self):
        """ Trying the quoting thing. """
        @contract
        def f(a, b):
            """ This is good
                :type a: ``int``
                :type b: ``int``
                :rtype: ``int``
            """
            pass

    def test_bad_quoting(self):
        def f(a, b):
            """
                :type a: ``int``
                :type b: ``int``
                :rtype: ``int`
            """
            pass

        self.assertRaises(ContractException, decorate, f)

    def test_bad_quoting2(self):
        def f(a, b):
            """
                :type a: ``int``
                :type b: `int``
                :rtype: ``int``
            """
            pass

        self.assertRaises(ContractException, decorate, f)

    def test_ok2(self):
        @contract(a='int', returns='int')
        def f(a, b):
            pass

    def test_invalid_args(self):
        def f():
            @contract(1)
            def g(a, b):
                return int(a + b)
        self.assertRaises(ContractException, f)

    def test_invalid_args2(self):
        """ unknown parameter """
        def f():
            @contract(c=2)
            def g(a, b):
                return int(a + b)
        self.assertRaises(ContractException, f)

    def test_check_it_works1(self):
        @contract(a='int', b='int', returns='int')
        def f(a, b):  # @UnusedVariable
            return 2.0
        self.assertRaises(ContractNotRespected, f, 1, 2)

    def test_check_it_works2(self):
        @contract(a='int', b='int', returns='int')
        def f(a, b):  # @UnusedVariable
            return a + b
        f(1, 2)
        self.assertRaises(ContractNotRespected, f, 1.0, 2)
        self.assertRaises(ContractNotRespected, f, 1, 2.0)

    def test_check_it_works2b(self):
        """ Nothing for b """
        @contract(a='int', returns='int')
        def f(a, b):  # @UnusedVariable
            return int(a + b)
        f(1, 2)
        f(1, 2.0)

    def test_check_it_works2c(self):
        """ Nothing for b """
        def f1(a, b):  # @UnusedVariable
            return int(a + b)

        f = decorate(f1, a='int', returns='int')

        f(1, 2)
        f(1, 2.0)
        self.assertRaises(ContractNotRespected, f, 1.0, 2)

    # def test_module_as_decorator(self):
    #     import contracts as contract_module
    #
    #     @contract_module
    #     def f(a, b): #@UnusedVariable
    #         return a + b
    #     f(1, 2)
    #     self.assertRaises(ContractNotRespected, f, 1.0, 2)

    def test_check_it_works3(self):
        @contract
        def f(a, b):
            """ This is good
                :type a: int
                :type b: int
                :rtype: int
            """
            return a + b
        f(1, 2)
        self.assertRaises(ContractNotRespected, f, 1.0, 2)
        self.assertRaises(ContractNotRespected, f, 1, 2.0)

    def test_inline_docstring_format_works(self):
        @contract
        def f(a, b):
            """ This is good
                :param int,>0 a: Description
                :param int,>0 b: Description
                :returns int,>0: Description
            """
            return a + b
        f(1, 2)
        self.assertRaises(ContractNotRespected, f, 1.0, 2)
        self.assertRaises(ContractNotRespected, f, -1, 2)

    def test_check_docstring_maintained(self):
        def f1(a, b):
            """ This is good
                :type a: int
                :type b: int
                :rtype: int
            """
            return a + b

        def f2(string):
            pass

        f1_dec = decorate(f1)
        self.assertNotEqual(f1.__doc__, f1_dec.__doc__)
        self.assertEqual(f1.__name__, f1_dec.__name__)
        self.assertEqual(f1.__module__, f1_dec.__module__)

        f2_dec = decorate(f2, string='str')
        self.assertNotEqual(f2.__doc__, f2_dec.__doc__)
        self.assertEqual(f2.__name__, f2_dec.__name__)
        self.assertEqual(f2.__module__, f2_dec.__module__)

        f1_dec_p = decorate(f1, modify_docstring=False)
        self.assertEqual(f1_dec_p.__doc__, f1.__doc__)

        f2_dec_p = decorate(f2, modify_docstring=False, string='str')
        self.assertEqual(f2.__doc__, f2_dec_p.__doc__)

        @contract
        def f1b(a, b):
            """ This is good
                :type a: int
                :type b: int
                :rtype: int
            """
            return a + b

        @contract(string='str')
        def f2b(string):
            pass

        @contract(modify_docstring=False)
        def f1b_p(a, b):
            """ This is good
                :type a: int
                :type b: int
                :rtype: int
            """
            return a + b

        @contract(modify_docstring=False, string='str')
        def f2b_p(string):
            pass

        self.assertNotEqual(f1.__doc__, f1b.__doc__)
        self.assertEqual(f1.__doc__, f1b_p.__doc__)
        self.assertNotEqual(f2.__doc__, f2b.__doc__)
        self.assertEqual(f2.__doc__, f2b_p.__doc__)

    def test_kwargs(self):
        def f(a, b, c=7):  # @UnusedVariable
            """ Same with optional
                :type a: int
                :type b: int
                :type c: int
            """
            if c != b:
                raise Exception()

        f2 = decorate(f)
        f2(0, 7)
        f2(0, 5, 5)
        self.assertRaises(Exception, f2, 0, 5, 4)
        self.assertRaises(Exception, f2, 0, 5)

    def test_varargs(self):
        def f(a, b, *c):
            """ Same with optional
                :type a: int
                :type b: int
                :type c: tuple
            """
            assert c == (a, b)

        f2 = decorate(f)
        f2(0, 7, 0, 7)

    def test_keywords(self):
        def f(A, B, **c):
            """ Same with optional
                :type A: int
                :type B: int
                :type c: dict
            """
            assert c['a'] == A
            assert c['b'] == B

        f2 = decorate(f)
        f(0, 7, a=0, b=7)
        f2(0, 7, a=0, b=7)

        self.assertRaises(Exception, f2, 0, 5, 0, 6)

    def test_same_signature(self):
        from inspect import getargspec

        def f(a):
            return a

        @contract(a='int')
        def f2(a):
            return a

        self.assertEqual(getargspec(f2), getargspec(f))


    def test_empty_types(self):

        def x():
            @contract
            def f(myparam):
                """
                :param myparam: something
                """

        self.assertRaises(MissingContract, x)

    def test_empty_types2(self):

        @contract
        def f(x):
            """
            :param x: something
            :type x: *
            """

        f(1)
