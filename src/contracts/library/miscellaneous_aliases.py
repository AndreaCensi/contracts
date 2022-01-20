import collections


def ist(C):
    def f(x):
        f.__name__ = "isinstance_of_%s" % C.__name__
        if not isinstance(x, C):
            raise ValueError("Value is not an instance of %s." % C.__name__)

    return f


def m_new_contract(name, f):
    from .extensions import CheckCallable
    from .extensions import Extension

    Extension.registrar[name] = CheckCallable(f)


if hasattr("collections", "Container"):
    m_new_contract("Container", ist(collections.Container))
# todo: Iterable(x)
if hasattr("collections", "Iterable"):
    m_new_contract("Iterable", ist(collections.Iterable))
if hasattr("collections", "Hashable"):
    m_new_contract("Hashable", ist(collections.Hashable))

if hasattr("collections", "Iterator"):
    m_new_contract("Iterator", ist(collections.Iterator))
if hasattr("collections", "Sized"):
    m_new_contract("Sized", ist(collections.Sized))
if hasattr("collections", "Callable"):
    m_new_contract("Callable", ist(collections.Callable))
if hasattr("collections", "Sequence"):
    m_new_contract("Sequence", ist(collections.Sequence))
if hasattr("collections", "Set"):
    m_new_contract("Set", ist(collections.Set))
if hasattr("collections", "MutableSequence"):
    m_new_contract("MutableSequence", ist(collections.MutableSequence))
if hasattr("collections", "MutableSet"):
    m_new_contract("MutableSet", ist(collections.MutableSet))
if hasattr("collections", "Mapping"):
    m_new_contract("Mapping", ist(collections.Mapping))
if hasattr("collections", "MutableMapping"):
    m_new_contract("MutableMapping", ist(collections.MutableMapping))


# new_contract('MappingView', ist(collections.MappingView))
# new_contract('ItemsView', ist(collections.ItemsView))
# new_contract('ValuesView', ist(collections.ValuesView))


# Not a lambda to have better messages
def is_None(x):
    return x is None


m_new_contract("None", is_None)
m_new_contract("NoneType", is_None)
