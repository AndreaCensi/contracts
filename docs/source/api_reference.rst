.. include:: definitions.txt

.. include:: menu.txt

.. _api_reference:

PyContracts public API reference
================================

This section provides a reference to |pycontracts|' public interface.

- See :ref:`api` for a more friendly discussion.
- See :ref:`contracts_language_reference` for a reference on the domain-specific language.


.. py:module:: contracts

Decorating a function
---------------------

.. autofunction:: contract

.. autofunction:: decorate


Enabling/disabling
------------------

.. autofunction:: disable_all


Exceptions
----------

.. autoclass:: ContractException

.. autoclass:: ContractSyntaxError

.. autoclass:: ContractNotRespected


Manually checking values
------------------------

.. autofunction:: check

.. autofunction:: check_multiple

.. autofunction:: parse

.. autofunction:: new_contract

.. autoclass:: Contract

   .. automethod:: check

   .. automethod:: fail

   .. automethod:: __repr__()

   .. automethod:: __str__()    

Miscellaneous
------------------------

.. py:data:: contract_expression

   A PyParsing expression that can be used to include
   contracts expression in your own PyParsing grammar.

.. include:: menu.txt
