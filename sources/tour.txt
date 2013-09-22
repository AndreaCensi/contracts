.. include:: definitions.txt

.. include:: menu.txt

.. _quick_tour:

Quick tour
--------------

The contracts are specified using the ``type`` clause of RST-style
docstrings (now accepted as standard in the python libraries); or, they can be passed explicitly
to the ``@contract`` decorator. In this example, |pycontracts| is smart enough to check that
the two parameters ``a`` and ``b`` are matrices of compatible dimensions. Then, it checks that
the result value is of compatible dimensions as well. ::

    import numpy
    from contracts import contract
    
    @contract
    def matrix_multiply(a,  b):
        ''' Multiplies two matrices together.
        
            :param a: The first matrix. Must be a 2D array.
             :type a: array[MxN],M>0,N>0
            
            :param b: The second matrix. Must be of compatible dimensions.
             :type b: array[NxP],P>0

              :rtype: array[MxP]
        '''
        return numpy.dot(a, b)

|pycontracts| can come in handy when you have operations
that could be one-liners if you are sure of the types of
the parameters, but doing all the checking adds to the 
complexity of the code.  


..
    @contract(players="dict(str: tuple(str, number))", returns="tuple(str,number)")
    def get_larger(players):
        ''' Find the best player in the league and its team, given
            a dictionary of name -> (team, score).
        '''
        # one-liner if we don't have to check
        ...
        
In the next example we check that: 

- The two lists have elements of the same type (indicated by the variable ``x``); 

- The returned list has the correct size (the sum of the two lengths). ::
    
    @contract(      a='list[ M ](type(x))', 
                     b='list[ N ](type(x))', 
               returns='list[M+N](type(x))')
    def my_cat_equal(a, b):
        ''' Concatenate two lists together. '''
        return a + b
    
The philosophy is to make the simple cases easy, and the difficult
possible, while still retaining readability.

For example, we can either ask for a simple list,
or specify more about it using the additional clauses.

.. list-table::
   :widths: 50 50
   :header-rows: 1

   * - Contract expression
     - Meaning
   * - ``list``
     - An instance of ``list``.
   * - ``list[2]``
     - A list of two elements.
   * - ``list(int)``
     - A list of integers.
   * - ``list(number)``
     - A list of numbers.
   * - ``list[3](number)``
     - A list of exactly three numbers. 
   * - ``list[>=3](number)``
     - A list of at least three numbers.
   * - ``list[>=3](number, >0)``
     - A list of at least three numbers, greater than 0.

|pycontracts| supports the use of variables. 
There are two kinds of variables: lower-case letters (``a``, ``b``, ...)
are general-purpose variables, while upper-case letters (``A``, ``B``, ...)
are constrained to bind to integer types; they are meant to represent
sizes and shapes. Moreover, |pycontracts| can do arithmetic and comparisons.

.. list-table::
   :widths: 50 50
   :header-rows: 1

   * - Contract expression
     - Meaning

   * - ``tuple(list[N], list[N])``
     - A tuple with two lists of the same length.

   * - ``tuple(list[N], list[M]), N<M``
     - A tuple with two lists, the first one being shorter.

   * - ``list[>0](type(x))``
     - A non-empty list containing elements of all the same type. 

   * - ``tuple(list(type(x)), list(type(x)))``
     - A tuple with two lists containing objects of the same type.


For the complete reference to the available contract expressions, see :ref:`contracts_language_reference`.

.. include:: menu.txt
