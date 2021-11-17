from contracts.test_registrar import fail, good

good("Container", [])
fail("Container", 1)
good("Hashable", 1)
# counterexample?
good("Iterable", [])
fail("Iterable", 1)
good("Iterable", {})
good("Iterator", [].__iter__())
fail("Iterator", [])
good("Sized", [])
good("Sized", {})
fail("Sized", lambda: None)
good("Sized", "")
good("Callable", lambda: None)
fail("Callable", [])
good("Sequence", [])
good("Sequence", (1,))
good("Sequence", "")
fail("Sequence", {})
good("Set", set([]))
fail("Set", [])
good("MutableSequence", [])
fail("MutableSequence", (1,))
good("MutableSet", set([]))
fail("MutableSet", frozenset([]))
good("Mapping", {})
fail("Mapping", [])
good("MutableMapping", {})
# good('MappingView', {}.keys())
# good('ItemsView', {}.items())
# good('ValuesView', {}.values())
