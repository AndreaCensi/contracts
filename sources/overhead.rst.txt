.. include:: definitions.txt

.. include:: menu.txt

.. _overhead:

PyContracts overhead in production and in testing
-------------------------------------------------

In production, all checks can be disabled using the function ``contracts.disable_all()``. 

All checks can also be disabled via the ``DISABLE_CONTRACTS`` environment variable. If the variable is defined, then checks are disabled and cannot be enabled via ``contracts.enable_all()``.

Overhead when disabled
^^^^^^^^^^^^^^^^^^^^^^

The performance in disabled mode depends on whether ``contracts.disable_all()`` is called before or after the decorated function is loaded.

If ``disable_all()`` is called *before*, then the decorator gets ignored and the overhead is 0. Example: ::

    contracts.disable_all()
    
    @contract(x='int,>=0', returns='int,>=1')
    def f(x):
        return x + 1

    f(0) # no overhead

If ``disable_all()`` is called *after*, then there is some overhead, because PyContracts will call the function as ``f(*args,**kwargs)``, which has some overhead. Example: ::

    @contract(x='int,>=0', returns='int,>=1')
    def f(x):
        return x + 1

    contracts.disable_all()
    
    f(0) # some overhead


Performance hit when enabled
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

I haven't done any rigorous benchmarking,  but PyContract's performance hit depends mainly on two factors:

1) PyContracts calls ``inspect``  methods to associate arguments to arguments names. This takes a surprising amount of time and probably there is a smarter way to do it.

2) The time to check the contract for each argument. This depends on the complexity of the contract. 

   Each contract is parsed only once and then represented as a syntactic tree. For example, the representation of ``int,>0`` is: ::

       python -c "import contracts; print '%r' % contracts.parse('int,>=0')"
       And([CheckType(int), CheckOrder(None,'>=',SimpleRValue(0))])
    
   Python being Python, there's some overhead for calling object methods in the contract tree.

.. include:: menu.txt
