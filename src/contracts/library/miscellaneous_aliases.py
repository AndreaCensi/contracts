import collections



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
    

m_new_contract('Container', ist(collections.Container))
# todo: Iterable(x)
m_new_contract('Iterable', ist(collections.Iterable))

m_new_contract('Hashable', ist(collections.Hashable))



m_new_contract('Iterator', ist(collections.Iterator))
m_new_contract('Sized', ist(collections.Sized))
m_new_contract('Callable', ist(collections.Callable))
m_new_contract('Sequence', ist(collections.Sequence))
m_new_contract('Set', ist(collections.Set))
m_new_contract('MutableSequence', ist(collections.MutableSequence))
m_new_contract('MutableSet', ist(collections.MutableSet))
m_new_contract('Mapping', ist(collections.Mapping))
m_new_contract('MutableMapping', ist(collections.MutableMapping))
#new_contract('MappingView', ist(collections.MappingView))
#new_contract('ItemsView', ist(collections.ItemsView))
#new_contract('ValuesView', ist(collections.ValuesView))


# Not a lambda to have better messages
def is_None(x): 
    return x is None

m_new_contract('None', is_None)
m_new_contract('NoneType', is_None)
