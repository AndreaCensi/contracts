
__all__ = ['MyAttribute']

class MyAttribute():
    """ Attribute is a descriptor for object attributes that
        enforces a check on any object the attribute is set
        to.
        
        Usage example:
        
from contracts import Attribute, ContractNotRespected

class spam(object): 
    x=Attribute('float,>0')         
    
eggs=spam()                                                             

print "Attempting eggs.x=1.0" 
eggs.x=1.0
print "eggs.x=" + str(eggs.x) 

print "Attempting eggs.x=-1.0" 
try:                                                                    
   eggs.x=-1.0                  
except ContractNotRespected as detail:                                  
   print detail                     
    """

    def __init__(self, check_string):
        from contracts.enabling import all_disabled
        if all_disabled():
            return
        
        self.check_string = check_string
        
    def __get__(self, instance, owner):
        if not hasattr(instance, '__contracts__'):
            instance.__contracts__ = {}

        if self not in instance.__contracts__:
            raise AttributeError("Attribute not set yet.")

        return instance.__contracts__.get(self)
        # return the stored data.

    def __set__(self, instance, value):
        if not hasattr(instance, '__contracts__'):
            instance.__contracts__ = {}

        from contracts.enabling import all_disabled
        from contracts.main import check
        
        if not all_disabled():
            check(self.check_string,value)

        instance.__contracts__[self] = value 