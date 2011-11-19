.. raw:: html
   :file: fork.html

.. include:: definitions.txt

.. py:currentmodule:: contracts

PyContracts
===========

|pycontracts| is a Python package that allows to declare constraints on function parameters and
return values. It supports a basic type system, variables binding, arithmetic constraints, and
has several specialized contracts (notably for Numpy arrays). 


**Status:** |pycontracts| is very well tested and documented. The last release
is version 1.2.0 (November 2011). See :ref:`changelog <changelog>`.


**Why**: The purpose of |pycontracts| is **not** to turn Python into a statically-typed language
(albeit you can be as strict as you wish), but, rather, to avoid the time-consuming and
obfuscating checking of various preconditions. In fact, more than the type constraints, I found
useful the ability to impose value and size constraints. For example, "I need a list of at least
3 positive numbers" can be expressed as ``list[>=3](number, >0))``. If you find that
|pycontracts| is overkill for you, you might want to try a simpler alternative, such as
typecheck_. If you find that |pycontracts| is not *enough* for you, you probably want to be
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

as well as hooks to extend |pycontracts| with new contracts types: ::

    new_contract('valid_name', lambda s: isinstance(s, str) and len(s)>0)
    check('dict(int: (valid_name, int))', employees)


**Support**: use the GitHub issue tracker_ or email me_.

**Documentation index**

- :ref:`installation`
- :ref:`quick_tour`
- :ref:`api`
- :ref:`contracts_language_reference`
- :ref:`api_reference`
- :ref:`credits`

.. _typecheck: http://oakwinter.com/code/typecheck/
.. _Haskell: http://www.haskell.org/
.. _tracker: http://github.com/AndreaCensi/contracts/issues

.. _me: http://www.cds.caltech.edu/~andrea/


.. _installation:

Installation
------------

Install |pycontracts| using: ::

    $ pip install PyContracts
    
or from GitHub: ::

    $ git clone git://github.com:AndreaCensi/contracts.git
    $ cd contracts
    $ python setup.py develop
    $ nosetests -w src         # run the extensive test suite

The beautiful library pyparsing_ is required.



.. include:: tour.txt

.. include:: api.txt

.. include:: reference.txt

.. include:: api_reference.txt


 
.. raw:: html
   :file: tracking.html


