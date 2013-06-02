from .main import contracts_decorate
from .utils import indent
from abc import ABCMeta
from contracts import ContractException
from types import FunctionType
import traceback


__all__ = ['ContractsMeta']


def is_function_or_static(f):
    is_normal_function = isinstance(f, FunctionType)
    is_staticmethod = isinstance(f, staticmethod)
    is_classmethod = isinstance(f, classmethod)
    return is_normal_function or is_staticmethod or is_classmethod
    
class ContractsMeta(ABCMeta):
    """ 
        This metaclass lets the subclasses inherit the specifications. 
        Very useful for abstract commands.
    
    """

    def __init__(cls, clsname, bases, clsdict):  # @UnusedVariable @NoSelf
        ABCMeta.__init__(cls, clsname, bases, clsdict)
        
        for k, f in clsdict.items():
            is_normal_function = isinstance(f, FunctionType)
            is_staticmethod = isinstance(f, staticmethod)
            is_classmethod = isinstance(f, classmethod)
            
            if not (is_normal_function or is_staticmethod or is_classmethod):
                # print('skipping %s:%s, %s' % (clsname, k, f))
                continue
            if k == '__init__': 
                continue
            
            this_function = '%s:%s()' % (clsname, k)  # @UnusedVariable
            # print('considering %s' % this_function)

            superclasses = cls.mro()[1:]
            for b in superclasses:
                if k in b.__dict__:
                    f0 = b.__dict__[k]
                    if is_function_or_static(f0):
                        if isinstance(f0, classmethod):
                            # print('found ancestor classmethod')
                            pass
                        elif isinstance(f0, staticmethod):
                            # print('found ancestor staticmethod')
                            pass
                        else:
                            assert isinstance(f0, FunctionType)
                            if '__contracts__' in f0.__dict__:
                                spec = f0.__contracts__
                                # msg = 'inherit contracts for %s:%s() from %s' % (clsname, k, b.__name__)
                                # print(msg)
                                # TODO: check that the contracts are a subtype
                                try:
                                    f1 = contracts_decorate(f, **spec)
                                except ContractException as e:
                                    msg = 'Error while applying ContractsMeta magic.\n'
                                    msg += '  subclass:  %s\n' % clsname
                                    msg += '      base:  %s\n' % b.__name__
                                    msg += '  function:  %s()\n' % k
                                    msg += 'Exception:\n'
                                    msg += indent(traceback.format_exc(e), '| ') + '\n'
                                    msg += '(most likely parameters names are different?)'
                                    raise ContractException(msg)       
                                setattr(cls, k, f1)
                                break
                    else:
                        pass
                else:
                    # print(' X not found in %s' % b.__name__)
                    pass
                    
                        
            else:
                pass
                # print(' -> No inheritance for %s' % this_function)
        
