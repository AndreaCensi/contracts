.. include:: definitions.txt

.. include:: menu.txt

.. _the_changelog:

Changelog
=========

.. _changelog:

1.8 -- 2017-09-24
-----------------

Summary of changes:

* Added "a^b" notation (Stefan Ulbrich) - needs tests.

* now logging.basicConfig() is not changed anymore.

* contracts for file-like objects (Jonathan Sharpe)

* Disabled the line ".library import miscellaneous_aliases"; things
  that were not documented and nobody missed.

* Many little improvements in the way errors are visualized.

* Moved to twine.



1.7.7 -- 2016-02-03
-------------------

* Not operator ``!``.

1.7.6 -- 2015-06-01
-------------------

* Full Python 3 support.

* Now contract strings can be unicode.

* Clarified the semantics of ``$`` when referring to types.


This does what is expected: ::

    from module import MyClass

    @contract(x='list($MyClass)')
    def f(x):
      pass


1.7.2 -- 2015-05-01
-------------------

* Better Python 3 support; metaclasses now supported on Python 3.2. Python 3.3 has problems with PyParsing probably due to randomization of data structures.

1.7.1 -- 2014-11-30
--------------------
* Fixed regressions on tests for contracts with arguments.


1.7.0 -- 2014-11-20
--------------------

* Implemented custom contracts with arguments (@ChrisBeaumont): ::

     @new_contract
     def greater_than(value, thresh):
         return value > thresh

     @contract(x='greater_than(3)'')
     def f(x):
         ...

* Implemented variable binding from Python scope (@ChrisBeaumont): ::

      a = 1

      @contract(x='>$a')
      def f(x):
          ...


1.6.5 -- 2014-09-11
-------------------

* If ``disable_all()`` is checked, ``check()`` does not anything.
  (contributed by Calen Pennington / cpennington)

1.6.1 to 1.6.4
--------------

Mainly performance improvements and cosmetic changes.

1.6.0 -- 2013-09-10
-------------------

* New features:
  - New ContractsMeta metaclass to provide subclasses with contracts. Use like you would ABCMeta. See docs:  :ref:`contractsmeta`
  - Added a "isinstance(ClassName)" contract for generic type checking

* Other fixes:
  - Cleaned up much of the code regarding Numpy arrays
  - Fixed a few incompatibilities with new versions of pyparsing
  - Better display of error conditions in several occasions.

* Incomplete list of contributors: Ryan Heimbuch


1.5.0 -- 2013-02-07
-------------------

* New "attr(name:type)" syntax for checking types of attributes.
  (Contributed by Brett Graham)
* Fixed handling of missing specs in docstrings.
* Numpy types are treated as numbers in comparisons.

1.4.0 -- 2012-07-15
-------------------

* Various minor internal improvements on speed and better error messages
* Introduced new "string" and "unicode" keywords (due to Xion) and
  clarified the meaning of strings in general.

New behavior:

* "unicode" matches unicode strings (only in 2.x)
* "str" matches the "str" type only (so ANSI strings in 2.x and all/Unicode strings in 3.x)
* "string" matches both str and unicode in 2.x and just "str" in 3.X

Because the new behavior should not break any existing usage,
this remains a "1.x" release.


1.2.0 -- 2011-09-01
--------------------

* Mainly speed improvements.

1.1.0 -- 2011-06-30
--------------------

* Now Numpy array are treated as sequences: ``seq[2](number)`` matches both ``[1,2]``
  as well as ``np.array([1,2])``.

1.0.0 -- 2011-06-30
--------------------

No new features since 0.9.4, mainly performance improvements and some bug fixes.

Main changes:

* Fixed bug that did not allow to define new contracts with name such as `list_`` if ``list``
  is already defined.

* Performance much improved when contracts is disabled; now the overhead is only an extra function call.



0.9.4 -- 2011-03-19
--------------------

Bug fixes:

* Fixed bugs with ``new_contract`` with new contract names composed
  by only two letters (it confused the parsing rules).

Performance improvements:

* Avoid deep copy of objects in some cases (thanks to William Furr),

New experimental features:

* Contracts for class methods (suggestion by William Furr).
  Documentation still to write; here's an example: ::

    from contracts import new_contract, contract

    class Game(object):
        def __init__(self, legal_moves):
            self.legal_moves = legal_moves

        # You can now create a contract from object methods
        # that can use the object attributes to validate the value.
        @new_contract
        def legal_move(self, move):
            if not move in self.legal_moves:
                raise ValueError('Move not valid')

        @contract(move='legal_move')
        def take_turn(self, move):
            pass

    game = Game(legal_moves=[1,2,3])
    game.take_turn(1) # ok
    game.take_turn(5) # raises exception



0.9.3 -- 2011-01-28
--------------------

New features:

* Interface change: the decorator is now called ``contract`` instead of ``contracts``,
  because ``from contracts import contracts`` looked quite clumsy
  (the old form is still available).

* The ``@contract`` decorator now changes the function's docstring to show the contracts for the parameters. See `an example application`__.

* Implemented the generic contracts ``seq`` and ``map`` that
  generalize ``list`` and ``dict`` when any Sequence or Mapping will do.

* Added element-by-element tests in ``array``. Now in an expression of the
  kind ``array(>=0|<-1)`` the expression will be evaluate element by element.

* Implemented ``pi`` as a special constant that can be used in the contracts.

* Now it is possible to give more context to calls to ``check`` and ``fail``
  through the use of keywords variable. For example::

      check('array[*xM]', a,  M=2)

* Added a function ``disable_all()`` that disables all testing done by PyContracts.
  This can be used to make sure that PyContracts is not slowing things down.

Various fixes:

* Fixed missing files in source distribution (thanks to Bernhard Biskup).

* Much better error messages.

* The functions signatures are now conserved  (using the ``decorator`` module).

* ``Contract`` objects and Exceptions can be safely pickled.

* In many cases, the exceptions are caught and re-raised to give a clearer stack trace.


.. __: http://andreacensi.github.com/geometry/api.html


0.9.2 -- Released 2010-12-27
----------------------------

(changelog not available)

.. include:: menu.txt
