.. include:: definitions.txt

.. include:: menu.txt

.. _api:

API for specifying contracts
============================

This is a discussion of the |pycontracts| API. 

- See :py:mod:`contracts` for a detailed list of this module's public interface.

- See :ref:`contracts_language_reference` for a description of the domain specific language
  used to describe the contracts.



Using the ``@contract`` decorator.
----------------------------------------------------

The decorator :py:func:`contracts` is the main way to 
define constraints. It is quite flexible, and it is smart enough 
to support functions with variable number of arguments and keyword arguments.

There are three ways to specify the contracts. In order of precedence:

- As arguments to this decorator. 
- As Python 3 function annotations.
- Using ``:type:`` and ``:rtype:`` tags in the function's docstring.

|pycontracts| will try these options in order. Note that, in any case,
only one of these options are chosen. For example, you cannot
use both annotations and docstring for the same function: if annotations
are found, the docstring is not considered.


Using decorator arguments
^^^^^^^^^^^^^^^^^^^^^^^^^

:py:func:`contract` accepts a list of keyword arguments.
Each keyword should correspond to one function argument, plus
the special name ``returns`` is reserved for describing the return value.
An example use would be: ::

    from contracts import contract

    @contract(a='int,>0', b='list[N],N>0', returns='list[N]')
    def my_function(a, b):
        ...
      

The values can be either:

- Strings using |pycontracts|' DSL language (see :ref:`contracts_language_reference`)

- Python types --- in this case |pycontracts| will do a simple :py:func:`isinstance` check.
  This is slightly more clear if the contract is simple: ::

      @contract(a=int, b=float, returns=float)
      def my_function(a, b):
          return a + b


Using Python annotations
^^^^^^^^^^^^^^^^^^^^^^^^

The same rules apply. In this case the syntax would look like this: ::

    from contracts import contract

    @contract
    def my_function(a:'int,>0', b:'list[N],N>0') -> 'list[N]': 
        ...
      


Using functions docstrings
^^^^^^^^^^^^^^^^^^^^^^^^^^

The Python standard library seems to have standardized on the ``:param:``, ``:type:``,
``:return:``, ``:rtype:`` tags to document functions, and tools like Sphinx
can interpret those tags to produce pretty documentation.

|pycontracts| can read contracts declared using the ``:type:`` and ``:rtype:`` tags.
In this way, your function becomes automatically more robust and better documented. 

Here is an example use: ::

    from contracts import contract
    
    @contract
    def my_function(a, b): 
      """ Function description.
  
          :param a: first number
          :type a: int,>0
          :param b: description of b
          :type b: list[N],N>0
      
          :return: a list
          :rtype: list[N]               """
      ...
          
          
.. note:: By convention, those annotations must be parsable as
    reStructuredText. 
    If the contract string has special RST characters in it, like ``*``,
    you can include it in double ticks. |pycontracts| will remove
    the double ticks before interpreting the string.

    For example, the two annotations in this docstring are equivalent
    for |pycontracts|, but the latter is better for Sphinx: ::

      """ My function 
  
          :param a: First parameter
          :type a: list(tuple(str,*))
      
          :param b: First parameter
          :type b: ``list(tuple(str,*))``
      """


.. include:: menu.txt

