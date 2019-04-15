from collections import Container, Iterable, Hashable, Iterator, \
    Sized, Callable, Sequence, Set, MutableSequence, MutableSet, Mapping, MutableMapping




def ist(C):
    def f(x):
        f.__name__ = 'isinstance_of_%s' % C.__name__
        if not isinstance(x, C):
            raise ValueError('Value is not an instance of %s.' % C.__name__)
    return f


def m_new_contract(name, f):
    from contracts.library.extensions import CheckCallable
    from contracts.library.extensions import Extension
    Extension.registrar[name] = CheckCallable(f)
    

m_new_contract('Container', ist(Container))
# todo: Iterable(x)
m_new_contract('Iterable', ist(Iterable))

m_new_contract('Hashable', ist(Hashable))



m_new_contract('Iterator', ist(Iterator))
m_new_contract('Sized', ist(Sized))
m_new_contract('Callable', ist(Callable))
m_new_contract('Sequence', ist(Sequence))
m_new_contract('Set', ist(Set))
m_new_contract('MutableSequence', ist(MutableSequence))
m_new_contract('MutableSet', ist(MutableSet))
m_new_contract('Mapping', ist(Mapping))
m_new_contract('MutableMapping', ist(MutableMapping))
#new_contract('MappingView', ist(collections.MappingView))
#new_contract('ItemsView', ist(collections.ItemsView))
#new_contract('ValuesView', ist(collections.ValuesView))


# Not a lambda to have better messages
def is_None(x): 
    return x is None

m_new_contract('None', is_None)
m_new_contract('NoneType', is_None)
