PyContracts
===========

PyContracts is a Python package that allows to declare constraints on function parameters
and return values. It supports a basic type system, variables binding, 
arithmetic constraints, and has several specialized contracts (notably for Numpy arrays). 
Pycontracts can parse the contracts specified in RST docstrings (using the standard ``:type:`` and ``:rtype`` constructs);
that way, your code is automatically documented.

The purpose of pycontracts is **not** to turn Python into a statically-typed language (albeit you can
be as strict as you wish), but, rather, to avoid the time-consuming and obfuscating checking of 
various preconditions.
In fact, more than the type constraints, I found useful the ability to impose value and size constraints.
For example, "I need a list of at least 3 positive numbers" can be expressed as ``list[>=3](number, >0))``.

**Installation** Install pycontracts using: ::

	$ pip install contracts
	
or from github (project page):

	$ git clone git@github.com:AndreaCensi/contracts.git
	$ cd contracts
	$ python setup.py develop
	$ nosetests -w src         # run the extensive test suite

The beautiful library pyparsing_ is required.

.. _pyparsing: 

XXX: read-only?


**Example.** This is an example of use. The contracts are specified using the ``type`` clause
of RST-style docstrings (now accepted as standard in the python libraries); or, they can
be passed explicitly to the ``@contracts`` decorator. 
In this example, pycontracts is smart enough to check that 
the two parameters ``a`` and ``b`` are matrices of compatible dimensions. 
Then, it checks that the result value is of compatible dimensions as well. ::

	import numpy
	from contracts import contracts
	
	@contracts
	def matrix_multiply(a,b):
		'''
			Multiplies two matrices together.
		
			:param a: The first matrix. Must be a 2D array.
			:type a: array[MxN],M>0,N>0
			
			:param b: The second matrix. Must be of compatible dimensions.
			:type b: array[NxP],P>0

			:return: The product of the two matrices.
			:rtype: array[MxP]
			
		'''
		return numpy.dot(a, b)

Pycontracts can come in handy when you have operations
that could be one-liners if you are sure of the types of
the parameters, but doing all the checking adds to the 
complexity of the code. 

	@contracts
	def get_larger(players):
		'''
			Find the best player in the league.
			
			:param players: Dictionary name -> (team, score)
			:type players: dict(str: tuple(str, number))
			
			:return: Returns the name and the score of the best player.
			:rtype: tuple(str, number)
			
		'''
		TODO
		
Pycontracts can do simple arithmetic. For example, in the 
next example we check that 1) the two lists have elements
of the same type; and 2) the returned list has the correct size.
	
	@contracts
	def cat(a, b):
		'''
			Concatenate two lists together.
			
			:type a: list[N](type(x))
			:type b: list[M](type(x))
			:rtype: list[M+N](type(x))
			
		'''
		return a + b



If you find that pycontracts is overkill for you, you might want to try simpler alternatives.

http://sandersn.com/blog//index.php/2008/05/27/python_type_checking

http://oakwinter.com/code/typecheck/

If you find that pycontracts is not enough for you, you probably want to be using Haskell_ instead of Python.


API
====================

Using decorators and docstrings
------------------------------------------------

Using decorators with explicit contracts.
------------------------------------------------

Decorate a function explicitly
------------------------------------------------

Using pycontracts for your own deeds
------------------------------------------------



Specifying contracts
====================

The next sections describe in details the various rules. 
Here we give a brief tour of what is possible. 

You can do simple arithmetic.

.. list-table::
   :widths: 30 70

   * - ``list``
     - An instance of ``list``.
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

Binding variables:

.. list-table::
   :widths: 30 70

   * - ``tuple(list[N], list[N])``
     - A tuple with two lists of the same length.

   * - ``tuple(list[N], list[M]),N<M``
     - A tuple with two lists, the first one being shorter.

   * - ``list[>0](type(x))``
     - A non-empty list containing elements of all the same type. 

   * - ``tuple(list(type(x)), list(type(x)))``
     - A tuple with two lists containing objects of the same type.


Display OR/AND

Simple types
------------

    dict, list, tuple, float, int, number, array, bool

    *
    
    
Equality
------------------

Just saying a value will match that value


Variables
---------

Integer variables::

    A B C D E F G H I J K L M N O P Q R S T U W V X Y Z

General-purpose variables::

    a b c d e f g h i j k l m n o p q r s t u w v x y z


Arithmetic and comparison
-------------------------


Lists
------------------

Tuples
------------------

Dictionaries
------------------

Numpy arrays
------------------


Advanced features
------------------

Context isolate
^^^^^^^^^^^^^^^ 

Other aliases
^^^^^^^^^^^^^

rgb, rgba


Under the hood
==============


expanding
----------


