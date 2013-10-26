from contracts import contract, new_contract

@new_contract
def my_condition(x):
    return x > 0

@contract(a='list(my_condition)')
def f1(a):
    pass

@contract
def f2(a):
    """
        :type a: list(my_condition)
    """
    pass

@contract
def f3(a):
    """
        You can also enclose the contract with RST code spec 
        if it creates problems.
        :type a: ``list(my_condition)``
    """
    pass

#f1([1,0])
#f2([1,0])
f3([1,0])
