Changelog
=========

.. _changelog: 

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
