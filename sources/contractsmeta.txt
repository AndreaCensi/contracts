.. include:: definitions.txt

.. include:: menu.txt

.. _contractsmeta:

Using the ``ContractsMeta`` meta-class
-------------------------------------------------

The  :py:class:`ContractsMeta` meta-class can be used as a drop-in 
replacement for ``ABCMeta``. It allows you to declare contracts
for a superclass and then have those contracts automatically
enforced for any class that derives from it.

For example, let us define a "timer" interface whose
``start`` method requires a positive number: ::

    from contracts import ContractsMeta, contract
    from abc import abstractmethod

    class TimerInterface():
        __metaclass__ = ContractsMeta

        @abstractmethod
        @contract(interval='(float|int),>0')
        def start(self, interval):
            pass

Now we can subclass  ``TimerInterface`` and all contracts
will be automatically inherited: ::

    class Timer(TimerInterface):
  
        def start(self, interval):
            time.sleep()


    t = Timer()
    t.start(-1) # raises ContractNotRespected

    # contracts.interface.ContractNotRespected: Breach for argument 'interval' to Timer:start().
    # Condition -1 >= 0 not respected
    # checking: >=0               for value: Instance of int: -1
    # checking: (float|int),>=0   for value: Instance of int: -1


.. include:: menu.txt
