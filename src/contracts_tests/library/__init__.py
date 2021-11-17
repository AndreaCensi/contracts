from . import (
    arithmetic_tc,
    attr_tc,
    collection_tc,
    comparison_tc,
    compositions_tc,
    dicts_tc,
    dummy_tc,
    extensions_tc,
    files_tc,
    isinstance_tc,
    lists_tc,
    map_tc,
    separate_context_tc,
    seq_tc,
    simple_values_tc,
    strings_tc,
    tuple_tc,
    types_tc,
    variables_tc,
)

try:
    import numpy
except ImportError:  # pragma: no cover
    pass
else:
    from . import array_tc
    from . import array_elements_tc
