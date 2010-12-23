import collections

from ..main import new_contract

# - add 'set' class
# - specialize with length:
def ist(C):
    def f(x):
        f.func_name = 'instanceof_%s' % C.__name__
        if not isinstance(x, C):
            raise ValueError('Value is not an instance of %s.' % C.__name__)
    return f
    
new_contract('Container', ist(collections.Container)) 
new_contract('Hashable', ist(collections.Hashable)) 
new_contract('Iterable', ist(collections.Iterable)) 
new_contract('Iterator', ist(collections.Iterator)) 
new_contract('Sized', ist(collections.Sized))
new_contract('Callable', ist(collections.Callable))
new_contract('Sequence', ist(collections.Sequence))
new_contract('Set', ist(collections.Set))
new_contract('MutableSequence', ist(collections.MutableSequence))
new_contract('MutableSet', ist(collections.MutableSet))
new_contract('Mapping', ist(collections.Mapping))
new_contract('MutableMapping', ist(collections.MutableMapping))
#new_contract('MappingView', ist(collections.MappingView))
#new_contract('ItemsView', ist(collections.ItemsView))
#new_contract('ValuesView', ist(collections.ValuesView))

new_contract('None', lambda x: x is None) 
new_contract('NoneType', lambda x: x is None) 