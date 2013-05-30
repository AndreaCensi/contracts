from . import good, fail, syntax_fail


class A(object):
    a = 1
    b = 2

tc_a = A()


class B(object):
    a = 2

tc_b = B()



syntax_fail('attr')  # need at least some attribute

good('attr(a:*)', tc_a)
good('attr(a:int)', tc_a)
good('attr(b:int)', tc_a)
good('attr(b:>1)', tc_a)
good('attr(b:int,>1)', tc_a)
fail('attr(b:int,<=1)', tc_a)

good('attr(a:*)', tc_b)
fail('attr(b:*)', tc_b)

good('attr(a:int;b:int)', tc_a)
good('attr(a:int;b:int)', tc_a)
good('attr(a:int;b:int,>1)', tc_a)
fail('attr(a:int;b:int,<=1)', tc_a)
