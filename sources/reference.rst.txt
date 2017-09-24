.. include:: definitions.txt

.. include:: menu.txt


.. _contracts_language_reference:

Language reference
================================

This section describes |pycontracts|' language for specifying contracts.

- See :ref:`quick_tour` for a summary of the available features.
- See :ref:`api` for a description of the API.


Simple types
------------

The simplest kind of contract consists in declaring the type 
of a value. These are the supported primitive types:  ::

    dict, list, tuple, float, int, number, array, bool, None

Moreover, there are two kinds of wild-cards:

``*``
  Matches any object.
  
``#``
  Never matches anything --- useful for debugging.
  

Variables
---------

|pycontracts| allows to use variables to bind to sub-expressions
and reuse later (it is simpler than it sounds).

There are two kinds of variables. The first kind is denoted
by an uppercase letter, and it is constrained to bind to integer values. :: 

    A B C D E F G H I J K L M N O P Q R S T U W V X Y Z

Lower-case letters denote general-purpose variables that can bind to any type::

    a b c d e f g h i j k l m n o p q r s t u w v x y z

.. note:: The reason for having specialized variables for integers is
   to encourage a writing style in which uppercase letters denote 
   lengths, shapes, etc. Moreover, an error will be thrown if they do not
   bind to integers, which helps in catching mistakes.



Scoped variables
---------------------------------------------

Contracts can refer to external variables using ``$PythonVariable``. For example, a typical application is the following: ::


    from module import MyClass
 
    @contract(x='list($MyClass)')
    def f(x):
      pass


.. include:: menu.txt

Logical expressions
-------------------

Two logical operators are supported:

AND
  Expressed with a comma (``,``).

  For example, the expression ::
   
      check("contract1,contract2", value)
      
  is roughly equivalent to ::
  
      check("contract1", value) and check("contract2", value)
      
  except that variables in the contracts are evaluated in the same context.
  
OR
  Expressed with a pipe symbol (``|``).
  
  The semantic is that the first matching expression is chosen.
  
  The expression: ::
  
      check("contract1|contract2", value) 
    
  is roughly equivalent to: ::
  
      if value respects "contract1":
         return True
      elif value respects "contract2":
         return True
      else: 
         return False
         

The AND has precedence over OR. For example, the expression ::

    a,b|c
    
is evaluated the same as ::

    (a, b) | c


.. list-table:: Examples of contracts with logical operators
   :widths: 50 50
   :header-rows: 1

   * - Contract expression
     - Meaning

   * - ``None|int``
     - Either None or an integer.



Equality
------------------

|towrite|


Arithmetic and comparison
-------------------------

|towrite|


Details of variable binding
---------------------------

|towrite|



Lists
------------------

You can specify that the value must be a list, and
specify optional constraints for its length and for its elements.

The general syntax is: ::

    list
    list[length_contract]
    list(elements_contract)
    list[length_contract](elements_contract)


.. list-table:: Examples of ``list`` contracts
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

   * - ``tuple(list[N], list[N])``
     - A tuple of two lists of the same length.
     
Sequences
------------------

The contract ``seq`` has the same syntax as ``list`` but matches any sequence. ::

    seq
    seq[length_contract]
    seq(elements_contract)
    seq[length_contract](elements_contract)


Tuples
------------------

You can either specify a length (with square brackets), 
or specify a contract for each element: ::
    
    tuple
    
    tuple[length]
    
    tuple(element1, ..., elementN)

In the latter case, you are also specifying implicitly the number of elements.


.. note:: The syntax for tuples is somewhat a special case. 
   While ``list(int,>0)`` signifies a list 
   of positive integers (or empty list), ``tuple(int, >0)``
   means a tuple with exactly 2 elements, the first of which 
   should be an integer, and the second must be positive (but not necessarily integer.)

.. list-table:: Examples of ``tuple`` contracts
   :widths: 50 50
   :header-rows: 1

   * - Contract expression
     - Meaning

   * - ``tuple``
     - A tuple.
     
   * - ``tuple[2]``
     - A tuple with two elements.

   * - ``tuple(*,*)``
     - A tuple with two elements.

   * - ``tuple(int)``
     - A tuple with one integer element.

   * - ``tuple(int, int)``
     - A tuple with two integer elements.

   * - ``tuple[>=2]``
     - A tuple with at least two elements.


Dictionaries
------------------

For dictionary, you can specify a length contract, as well as a contract 
for its keys and values: ::
    
    dict
    
    dict[length_contract]
    
    dict(key_contract: value_contract)
    
    dict[length_contract](key_contract: value_contract)


.. list-table:: Examples of ``dict`` contracts
   :widths: 50 50
   :header-rows: 1

   * - Contract expression
     - Meaning

   * - ``dict``
     - Any dictionary.

   * - ``dict[2]``
     - A dictionary with two elements.

   * - ``dict(*: *)``
     - Any dictionary.

   * - ``dict(*: int)``
     - A dictionary whose values are integers.

   * - ``dict(str: *)``
     - A dictionary whose keys are strings

   * - ``dict(str: tuple(type(x),type(y)) ), x!=y``
     - A dictionary whose keys are strings, and whose values
       are tuples with two elements, of two different types ``x`` and ``y``.

Mappings
--------

The contract ``map`` has the same syntax as ``dict`` but matches any mapping. ::

    map
    
    map[length_contract]
    
    map(key_contract: value_contract)
    
    map[length_contract](key_contract: value_contract)
    

Numpy arrays
------------------

The support for Numpy arrays was one of the motivations for me to develop |pycontracts|.
Numpy_ is one of the best and most useful Python packages around. It supports
the ndarray_ datatype which allows for operations with tensors_ of arbitrary dimensions.

All of that is very powerful, but it might be a bit confusing, especially 
because Numpy tends to be very liberal when it gets to operations between arrays.
For example, the operation ``A * B``, if ``A`` is a 2D matrix, is well defined
when ``B`` is a scalar, a vector, or a matrix. Sometimes you want to be certain
of your assumptions, otherwise you risk of ignoring powerful bugs. 

.. note:: Researchers tend to be a bit paranoid, because often
   you don't know what to expect out of your algorithms. A stupid
   bug can lead to an exciting (false) discovery!
   
So |pycontracts| offers several shortcuts for Numpy arrays, and
the error messages tend to be more descriptive.

The general syntax looks like this: ::

    array
    
    array[shape_contract]

    array(numpy_contract)
    
    array[shape_contract](numpy_contract)
   
   
Shape contracts
^^^^^^^^^^^^^^^^

A *shape contract* is specified using a special syntax of the kind:

    dimension1 x dimension2 x dimension3
    
    dimension1 x dimension2 x dimension3 x ...
    
The ellipsis is part of the syntax and specifies that more dimensions are allowed.

Each dimension can be specified as a number, with variables, or as a contract.


.. list-table:: Examples of ``array`` shape contracts
   :widths: 50 50
   :header-rows: 1

   * - Contract expression
     - Meaning

   * - ``array``
     - Any array.

   * - ``array[3]``
     - A 1D array with 3 elements (``shape=(3,)``).

   * - ``array[3x2]``
     - A 2D array with 3 rows and 2 columns (``shape=(3,2)``).

   * - ``array[3 x ...]``
     - A nD array with 3 rows and arbitrary other dimensions.

   * - ``array[3xN], N>=2``
     - A 2D array with 3 rows and at least 2 columns.

   * - ``array[NxN], N>0``
     - A square matrix.

   * - ``array[NxNx...], N>0``
     - A tensor with the first two dimensions of equal size.

   * - ``list(array[NxN]), N>0``
     - A list of square matrices of the same size.

Numpy-specific contracts
^^^^^^^^^^^^^^^^^^^^^^^^^

A *numpy contract* is special and implemented separately 
from the other |pycontracts| contract.
Right now, we support:

Datatype contracts
  These specify the datatype of the array. Available: ::
      
      uint8 uint16 uint32 uint64 int8 int16 int32  int64 float32 float64
      
Arithmetic comparisons
  These have the semantics that **all** elements must satisfy the contract.
  They appear similar to the normal |pycontracts| comparison: ::
  
      >0   <0   <=1   =0


.. list-table:: Examples of ``array`` elements contracts
   :widths: 50 50
   :header-rows: 1

   * - Contract expression
     - Meaning

   * - ``array``
     - Any array.

   * - ``array(>=0)``
     - An array with nonnegative elements.

   * - ``array(int8,>=0)``
     - An array with nonnegative integer elements.

   * - ``array[NxN](float,>=0,<=1)``
     - A square matrix with float elements in the interval [0,1].

   * - ``array[NxN](int,(0|1))``
     - A square matrix with each element equal either to 0 or 1 (this could model a directed graph).
     

Other examples
^^^^^^^^^^^^^^

Here is an example that first uses :py:func:`new_contract` to specify 
a domain-specific array type (``rgb``, ``rgba``), then uses |pycontracts|
to be sure that the two given images and the result values have coherent dimensions.
Notice how the contracts serve very well as documentation. ::

    from contracts import contract, new_contract
    
    new_contract('rgb',  'array[HxWx3](uint8),H>0,W>0')
    new_contract('rgba', 'array[HxWx4](uint8),H>0,W>0')
    
    @contract
    def blend_images(image1, image2):
        ''' 
             Blends two images together. 
    
             :param image1: The first image to blend.
             :type image1: rgb,array[HxWx*]
             
             :param image2: The second image to blend. Can have an alpha layer.
             :type image2: (rgb|rgba),array[HxWx*]
             
             :return: The blended image.
             :rtype: rgb,array[HxWx3]
        '''
        ...

If you want to have a function that accepts a list of images, you would write: ::

    @contract
    def blend_images(images):
        '''  
             Blends a series of images together.
    
             :type images: list[N](rgb,array[HxWx*]), N>=2

             :rtype: rgb,array[HxWx3]
        '''
        ...

.. _Numpy: http://numpy.scipy.org/

.. _ndarray: http://docs.scipy.org/doc/numpy/reference/generated/numpy.ndarray.html

.. _tensors: http://en.wikipedia.org/wiki/Tensor



Advanced topic: the context isolate operator
---------------------------------------------

|pycontracts| has a special construct ``$(...)`` used to separate the context
of variables. The semantics is that the variables assigned inside ``$(...)``
are not propagated outside.

.. list-table:: Examples of ``$()`` contracts
   :widths: 50 50
   :header-rows: 1

   * - Contract expression
     - Meaning

   * - ``list(tuple(type(x),type(y)),x!=y)``
     - A list whose elements
       are tuples with two elements, of two different types ``x`` and ``y``
       (``x`` and ``y`` are common among the list elements ).

   * - ``list( $( tuple(type(x),type(y)),x!=y) )``
     - A list whose elements
       are tuples with two elements, of two different types ``x`` and ``y``.
       (``x`` and ``y`` are not joined among the list elements ).

.. include:: menu.txt
