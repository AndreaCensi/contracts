from contracts import ContractsMeta, contract
from abc import abstractmethod

class TimerInterface():
    __metaclass__ = ContractsMeta

    @abstractmethod
    @contract(interval='(float|int),>=0')
    def start(self, interval):
        pass


class Timer(TimerInterface):
    
    def start(self, interval):
        time.sleep()


t = Timer()
t.start(-1) # raises ContractNotRespected

# contracts.interface.ContractNotRespected: Breach for argument 'interval' to Timer:start().
# Condition -1 >= 0 not respected
# checking: >=0               for value: Instance of int: -1
# checking: (float|int),>=0   for value: Instance of int: -1