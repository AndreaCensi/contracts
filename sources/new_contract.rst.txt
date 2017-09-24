.. include:: definitions.txt

.. include:: menu.txt

.. _new_contract:

Creating new contracts using ``new_contract``
-------------------------------------------------

The function  :py:func:`new_contract`  is used to define new contracts.
It takes two arguments. The first argument is the name
of the new contract, and the second is the value: ::

    new_contract('color', 'list[3](float)')

Once defined, the new contracts can be used as part of more complicated 
expressions: ::

    @contract(colors='list(color)')
    def average_colors(colors):
        pass

The second parameter to ``new_contract`` can be either
a string, a Python type, or a callable function. 

- If it is a string or a type, it is interpreted as contract expression
  like any parameter to :py:func:`@contract`.

- If it is a callable, it must accept one parameter, and either:
  
  * return True or None, to signify it accepts.
  
  * return False or raise ValueError, to signify it doesn't.
  
  If ValueError is raised, its message is used in the error.
  
This function returns a :py:class:`Contract` object. It might be
useful to check right away if the declaration is what you meant,
using :py:func:`Contract.check` and :py:func:`Contract.fail`.  

For example, suppose that you are writing a graphical application
and that many of your functions need arguments representing colors.
It might be a good idea to declare once and for all what is a color,
and then reuse that definition. For example: ::

    color = new_contract('color', 'list[3](number,>=0,<=1)')
    # Make sure we got it right
    color.check([0,0,0])
    color.check([0,0,1])
    color.fail([0,0])
    color.fail([0,0,2])
    
    # Now use ``color`` in other contracts.
    @contract
    def fill_area(inside, border):
        """ Fill the area inside the current figure.
        
            :type border: color
            :type inside: color              """
        ...
        
    @contract
    def fill_gradient(colors):
        """ Use a gradient to fill the area.
        
            :type colors: list[>=2](color)     """
        ...


.. include:: menu.txt