.. raw:: html
   :file: fork.html

.. include:: definitions.txt

PyContracts
===========

|pycontracts| is a Python package that allows to declare constraints on function parameters and
return values. It supports a basic type system, variables binding, arithmetic constraints, and
has several specialized contracts (notably for Numpy arrays). |pycontracts| can parse the
contracts specified in RST docstrings (using the standard ``:type:`` and ``:rtype`` constructs);
that way, your code is automatically documented.

The purpose of |pycontracts| is **not** to turn Python into a statically-typed language (albeit
you can be as strict as you wish), but, rather, to avoid the time-consuming and obfuscating
checking of various preconditions. In fact, more than the type constraints, I found useful the
ability to impose value and size constraints. For example, "I need a list of at least 3 positive
numbers" can be expressed as ``list[>=3](number, >0))``.

**Alternatives:** If you find that |pycontracts| is overkill for you, you might want to try a simpler alternative, such as typecheck_. If you find that |pycontracts| is not *enough* for you, you probably want to be using Haskell_ instead of Python.

.. _typecheck: http://oakwinter.com/code/typecheck/
.. _Haskell: http://www.haskell.org/


Installation
------------

Install |pycontracts| using: ::

    $ pip install contracts
    
or from GitHub: ::

    $ git clone git://github.com:AndreaCensi/contracts.git
    $ cd contracts
    $ python setup.py develop
    $ python setup.py nosetests    # run the extensive test suite

The beautiful library pyparsing_ is required.


Usage examples
--------------

The contracts are specified using the ``type`` clause of RST-style
docstrings (now accepted as standard in the python libraries); or, they can be passed explicitly
to the ``@contracts`` decorator. In this example, |pycontracts| is smart enough to check that
the two parameters ``a`` and ``b`` are matrices of compatible dimensions. Then, it checks that
the result value is of compatible dimensions as well. ::

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

              :rtype: array[MxP]
            
        '''
        return numpy.dot(a, b)

|pycontracts| can come in handy when you have operations
that could be one-liners if you are sure of the types of
the parameters, but doing all the checking adds to the 
complexity of the code.  


..
    @contracts
    def get_larger(players):
        '''
            Find the best player in the league.
            
            :param players: Dictionary name -> (team, score)
            :type players: dict(str: tuple(str, number))
            
            :return: Returns the name and the score.
            :rtype: tuple(str, number)
            
        '''
        ...
        
In the next example we check that 1) the two lists have elements
of the same type (indicated by the variable ``x``); 
and 2) the returned list has the correct size. ::
    
    @contracts
    def cat(a, b):
        '''
            Concatenate two lists together.
            
            :type a: list[N](type(x))
            :type b: list[M](type(x))
            :rtype: list[M+N](type(x))
            
        '''
        return a + b



.. include:: tour.txt

.. include:: api.txt

.. include:: reference.txt
 


