from contracts import contract, new_contract

class Foo(object):
    pass

new_contract('foo', Foo)

@contract(foo_list='list[>1](foo)')
def foo_list_func(foo_list):
    pass
    
# OK
foo_list_func([Foo(), Foo()])

# raises ContractNotRespected
foo_list_func([Foo(), 42])