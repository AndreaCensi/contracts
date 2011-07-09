PyContracts is a Python package that allows to declare constraints on function parameters and
return values. It supports a basic type system, variables binding, arithmetic constraints, and
has several specialized contracts (notably for Numpy arrays). 

A brief summary follows. See the full documentation at: <http://andreacensi.github.com/contracts/>

**Why**: The purpose of PyContracts is **not** to turn Python into a statically-typed language
(albeit you can be as strict as you wish), but, rather, to avoid the time-consuming and
obfuscating checking of various preconditions. In fact, more than the type constraints, I found
useful the ability to impose value and size constraints. For example, "I need a list of at least
3 positive numbers" can be expressed as ``list[>=3](number, >0))``. If you find that
PyContracts is overkill for you, you might want to try a simpler alternative, such as
typecheck_. If you find that PyContracts is not *enough* for you, you probably want to be
using Haskell_ instead of Python.


Contracts can be specified in three ways:

- Using annotations (for Python 3) ---this is perhaps the most 
  intuitive way: :: 
  
      @contract
      def my_function(a : 'int,>0', b : 'list[N],N>0') -> 'list[N]': 
           # Requires b to be a nonempty list, and the return 
           # value to have the same length.
           ...
      
- Using ``:type:`` and ``:rtype:`` tags in docstrings. In this way, they will be included
  in your Sphinx documentation: ::
   
      @contract
      def my_function(a, b): 
          """ Function description.
              :type a: int,>0
              :type b: list[N],N>0
              :rtype: list[N]
          """
          ...
          
- Using arguments to the decorators; the least intrusive way: ::
   
      @contract(a='int,>0', b='list[N],N>0', returns='list[N]')
      def my_function(a, b):
          ...
          
Moreover, there are utility functions for manual checking of values: ::

    check('array[HxWx3](uint8),H>10,W>10', image)

as well as hooks to extend PyContracts with new contracts types: ::

    new_contract('valid_name', lambda s: isinstance(s, str) and len(s)>0)
    check('dict(int: (valid_name, int))', employees)


.. _typecheck: http://oakwinter.com/code/typecheck/
.. _Haskell: http://www.haskell.org/

**Status:** PyContracts is very well tested and documented. The syntax is stable and it won't be changed.

