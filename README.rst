PyContracts is a Python package that allows to declare constraints on function parameters and
return values. It supports a basic type system, variables binding, arithmetic constraints, and
has several specialized contracts (notably for Numpy arrays). 


As a quick intro, please see `this presentation about PyContracts`_.

.. _`this presentation about PyContracts`: http://censi.mit.edu/pub/research/201410-pycontracts/201410-pycontracts.pdf 

.. image:: http://censi.mit.edu/pub/research/201410-pycontracts/201410-pycontracts.border.png
   :height: 100px
   :target: http://censi.mit.edu/pub/research/201410-pycontracts/201410-pycontracts.pdf 
   :alt: A presentation about PyContracts



.. container:: brief_summary
  
    A brief summary follows. See the full documentation at: <http://andreacensi.github.com/contracts/>


**Why**: The purpose of PyContracts is **not** to turn Python into a statically-typed language
(albeit you can be as strict as you wish), but, rather, to avoid the time-consuming and
obfuscating checking of various preconditions. In fact, more than the type constraints, I found
useful the ability to impose value and size constraints. For example, "I need a list of at least
3 positive numbers" can be expressed as ``list[>=3](number, >0))``. If you find that
PyContracts is overkill for you, you might want to try a simpler alternative, such as
typecheck_. If you find that PyContracts is not *enough* for you, you probably want to be
using Haskell_ instead of Python.

**Specifying contracts**: Contracts can be specified in three ways:

1. **Using the ``@contract`` decorator**: ::
   
      @contract(a='int,>0', b='list[N],N>0', returns='list[N]')
      def my_function(a, b):
          ...

2. **Using annotations** (for Python 3): :: 
  
      @contract
      def my_function(a : 'int,>0', b : 'list[N],N>0') -> 'list[N]': 
           # Requires b to be a nonempty list, and the return 
           # value to have the same length.
           ...
      
3. **Using docstrings**, with the ``:type:`` and ``:rtype:`` tags: ::
   
      @contract
      def my_function(a, b): 
          """ Function description.
              :type a: int,>0
              :type b: list[N],N>0
              :rtype: list[N]
          """
          ...
          
..
   In any case, PyContracts will include the spec in the ``__doc__`` attribute.

**Deployment**: In production, all checks can be disabled using the function ``contracts.disable_all()``, so the performance hit is 0.

**Extensions:** You can extend PyContracts with new contracts types: ::

    new_contract('valid_name', lambda s: isinstance(s, str) and len(s)>0)
    @contract(names='dict(int: (valid_name, int))')
    def process_accounting(records):
        ...

Any Python type is a contract: ::

    @contract(a=int, # simple contract
              b='int,>0' # more complicated
              )
    def f(a, b):
        ...

**Enforcing interfaces**:  ``ContractsMeta`` is a metaclass,
like ABCMeta, which propagates contracts to the subclasses: ::

    from contracts import contract, ContractsMeta, with_metaclass
    
    class Base(with_metaclass(ContractsMeta, object)):

        @abstractmethod
        @contract(probability='float,>=0,<=1')
        def sample(self, probability):
            pass

    class Derived(Base):
        # The contract above is automatically enforced, 
        # without this class having to know about PyContracts at all!
        def sample(self, probability):
            ....

**Numpy**: There is special support for Numpy: ::

    @contract(image='array[HxWx3](uint8),H>10,W>10')
    def recolor(image):
        ...

**Status:** The syntax is stable and it won't be changed. PyContracts is very well tested on Python 2.x. 

**Status on Python 3.x:** We reached feature parity! Everything works on Python 3 now.

**Contributors**:

- `Chris Beaumont`_ (Harvard-Smithsonian Center for Astrophysics): ``$var`` syntax; kwargs/args for extensions.
- `Brett Graham`_ (Rowland Institute at Harvard University):  ``attr(name:type)`` syntax for checking types of attributes.
- `William Furr`_: bug reports and performance improvements
- `Karol Kuczmarski`_ (Google Zurich):  implementation of "string" and "unicode" contracts
- `Maarten Derickx`_ (Leiden U.):  documentation fixes
- `Calen Pennington`_ (EdX):  disabling checks inside check() function.
- `Adam Palay`_ (EdX): implementation of environment variable enabling/disabling override.
- `Ryan Heimbuch`_:  bug reports 
- Bernhard Biskup:  bug reports
- `asharp`_: bug fixes
- `Dennis Kempin`_ (Google mothership): Sphinx-style constraints specs
- `Andy Hayden`_: Python 3 support, more efficient Numpy checks
- `Jonathan Sharpe`_: contracts for file-like objects, not operator

(Please let me know if I forgot anybody.)

.. _`Jonathan Sharpe`: http://jonathansharpe.me.uk/

.. _`Chris Beaumont`: http://chrisbeaumont.org/
.. _`asharp`:  https://github.com/asharp
.. _`Maarten Derickx`: http://mderickx.nl/
.. _`Ryan Heimbuch`: https://github.com/ryanheimbuch-wf
.. _`Calen Pennington`: https://github.com/cpennington
.. _`Adam Palay`: https://github.com/adampalay
.. _`William Furr`: http://www.ccs.neu.edu/home/furrwf/
.. _`Karol Kuczmarski`:  http://xion.org.pl/
.. _`Brett Graham`: https://github.com/braingram
.. _`Dennis Kempin`: https://github.com/denniskempin
.. _`Andy Hayden`: http://careers.stackoverflow.com/hayd

.. _typecheck: http://oakwinter.com/code/typecheck/
.. _Haskell: http://www.haskell.org/


