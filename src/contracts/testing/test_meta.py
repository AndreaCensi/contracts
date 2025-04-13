from abc import abstractmethod
import functools
import pytest

from contracts import ContractNotRespected, contract, ContractsMeta
from contracts import CannotDecorateClassmethods
from contracts import with_metaclass


class TestMeta:

    def test_meta_still_works1(self):

        class A(with_metaclass(ContractsMeta, object)):

            @abstractmethod
            @contract(a='>0')
            def f(self, a):
                pass

        class B(A):
            # does not implement f
            pass

        with pytest.raises(TypeError):
            B()

    def test_meta_still_works2(self):

        class A(with_metaclass(ContractsMeta, object)):

            # inverse order
            @contract(a='>0')
            @abstractmethod
            def f(self, a):
                pass

        class B(A):
            # does not implement f
            pass

        with pytest.raises(TypeError):
            B()

    def test_meta1(self):

        class A(with_metaclass(ContractsMeta, object)):

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

        with pytest.raises(ContractNotRespected):
            b.f(0)
        with pytest.raises(ContractNotRespected):
            b.g(0)

    @pytest.mark.xfail(reason="Known issue with static methods")
    def test_static1(self):

        class A(with_metaclass(ContractsMeta, object)):

            @staticmethod
            @contract(a='>0')
            def f(a):
                pass

        with pytest.raises(ContractNotRespected):
            A.f(0)

        class B(A):

            @staticmethod
            def f(a):
                pass

        with pytest.raises(ContractNotRespected):
            B.f(0)  # this doesn't work

    @pytest.mark.xfail(reason="Known issue with class methods")
    def test_classmethod1(self):

        class A(with_metaclass(ContractsMeta, object)):

            @classmethod
            @contract(a='>0')
            def f(cls, a):
                print('called A.f(%s)' % a)
                pass

        with pytest.raises(ContractNotRespected):
            A.f(0)

        class B(A):

            @classmethod
            def f(cls, a):
                print('called B.f(%s)' % a)
                pass

        with pytest.raises(ContractNotRespected):
            B.f(0)  # this doesn't work

    @pytest.mark.xfail(reason="Known issue with class methods")
    def test_classmethod1ns(self):

        class A(with_metaclass(ContractsMeta, object)):

            @classmethod
            @contract(a='>0')
            def f(cls, a):
                print('called A.f(%s)' % a)
                pass

        with pytest.raises(ContractNotRespected):
            A.f(0)

        class B(A):

            @classmethod
            def f(cls, a):
                print('called B.f(%s)' % a)
                pass

        with pytest.raises(ContractNotRespected):
            B.f(0)  # this doesn't work


    def test_classmethod2a(self):

        def test_classmethod2():

            class A(with_metaclass(ContractsMeta, object)):

                @contract(a='>0')
                @classmethod
                def f(cls, a):
                    pass

            class B(A):

                @classmethod
                def f(cls, a):
                    pass

        with pytest.raises(CannotDecorateClassmethods):
            test_classmethod2()



