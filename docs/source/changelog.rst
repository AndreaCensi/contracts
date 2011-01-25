
0.9.3 -- 2011-01-XX
--------------------

Document, pre-release:
* finish contracts --> contract
* document disable_all() (tests missing) 
* The function's docstring is now modified 


New features:

* The function's docstring is now modified to show the contracts for the parameters.

* Implemented the generic contracts ``seq`` and ``map`` that
  generalize ``list`` and ``dict`` when any Sequence or Mapping will do. 

* Added element-by-element tests in ``array``. Now in an expression of the
  kind ``array(>=0|<-1)`` the expression will be evaluate element-by-element.

* Implemented special value ``pi`` = 3.1415... 

* Interface change: the decorator is now called ``contract`` instead of ``contracts``,
  because ``from contracts import contracts`` looked quite clumsy
  (the old form is still available).

* Now it is possible to give more context to calls to ``check`` and ``fail`` 
  through the use of keywords variable. For example:: 
  
      check('array[*xM]', a,  M=2)

* Added a function ``disable_all()`` that disables  (tests missing) 

Fixes:

* Much better error messages.

* The functions signatures are now conserved, using the ``decorator`` module. 
      
* ``Contract`` objects can be safely pickled. 

* In many cases, the exceptions are caught and re-raised to give a clearer stack trace.


0.9.2 -- Released 2010-12-27
----------------------------

(changelog not available)
