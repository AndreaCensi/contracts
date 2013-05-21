from abc import ABCMeta
from types import FunctionType
from contracts.main import contracts_decorate

__all__ = ['ContractsMeta']


class ContractsMeta(ABCMeta):
    """ 
        This metaclass lets the subclasses inherit the specifications. 
        Very useful for abstract commands.
    
    """

    def __init__(cls, clsname, bases, clsdict):  # @UnusedVariable @NoSelf
        ABCMeta.__init__(cls, clsname, bases, clsdict)
        
        for k, f in clsdict.items():
            if not isinstance(f, FunctionType):
                continue
            if k == '__init__': 
                continue
            
            # this_function = '%s:%s()' % (clsname, k)  # @UnusedVariable
            
            # print('considering %s' % this_function)

            superclasses = cls.mro()[1:]
            for b in superclasses:
                if k in b.__dict__:
                    f0 = b.__dict__[k]
                    if isinstance(f0, FunctionType):
                        if '__contracts__' in f0.__dict__:
                            spec = f0.__contracts__
                            # msg = 'inherit contracts for %s:%s() from %s' % (clsname, k, b.__name__)
                            # print(msg)
                            # TODO: check that the contracts are a subtype
                            f1 = contracts_decorate(f, **spec)
                            setattr(cls, k, f1)
                            break
                    else:
                        pass
                else:
                    pass
                    # print(' X not found in %s' % b.__name__)
                        
            else:
                pass
                # print(' -> No inheritance for %s' % this_function)
        
