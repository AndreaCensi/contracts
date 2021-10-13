# cython: language_level=3, annotation_typing=True, c_string_encoding=utf-8, boundscheck=False, wraparound=False, initializedcheck=False
# class Extra:
#     loading = False
#
# def load_extra():
#     if not Extra.loading:
#         Extra.loading = True
# #         from . import useful_contracts
#         from .library import miscellaneous_aliases
#         # And after everything else is loaded, load the  utils
#     else:
#         print('already loading...')
from .syntax import ParseException
from .library.extensions import CheckCallableWithSelf
from .library import CheckCallable, Extension, SeparateContext, identifier_expression
from .inspection import can_accept_self, can_accept_at_least_one_argument
from .interface import Contract, ContractSyntaxError, Where, describe_value, ContractNotRespected
from .syntax import contract_expression
from .inspection import getfullargspec


class Storage:
    # Cache storage
    string2contract = {}


def _cacheable(string, c):
    """ Returns whether the contract c defined by string string is cacheable. """
    # XXX need a more general way of indicating
    #     whether a contract is safely cacheable
    return '$' not in string


def get_annotations(function):
    return getfullargspec(function).annotations


def get_all_arg_names(function):
    spec = getfullargspec(function)
    possible = spec.args + [spec.varargs, spec.varkw] + spec.kwonlyargs
    all_args = [x for x in possible if x]
    return all_args


def check_param_is_string(x):
    if not isinstance(x, str):
        msg = 'Expected a string, obtained %s' % type(x)
        raise ValueError(msg)


def new_contract_impl(identifier, condition):
    from .main import parse_flexible_spec
    # Be friendly
    if not isinstance(identifier, str):
        msg = 'I expect the identifier to be a string; received %s.' % describe_value(identifier)
        raise ValueError(msg)

    # Make sure it is not already an expression that we know.
    # (exception: allow redundant definitions. To this purpose,
    #   skip this test if the identifier is already known, and catch
    #   later if the condition changed.)
    if identifier in Extension.registrar:
        # already known as identifier; check later if the condition
        # remained the same.
        pass
    else:
        # check it does not redefine list, tuple, etc.
        try:
            c = parse_contract_string_actual(identifier)
            msg = ('Invalid identifier %r; it overwrites an already known '
                   'expression. In fact, I can parse it as %s (%r).' %
                   (identifier, c, c))
            raise ValueError(msg)
        except ContractSyntaxError:
            pass

    # Make sure it corresponds to our idea of identifier
    try:
        c = identifier_expression.parseString(identifier, parseAll=True)
    except ParseException as e:
        loc = e.loc
        if loc >= len(identifier):
            loc -= 1
        where = Where(identifier, character=loc)  # line=e.lineno, column=e.col)
        # msg = 'Error in parsing string: %s' % e
        msg = ('The given identifier %r does not correspond to my idea '
               'of what an identifier should look like;\n%s\n%s'
               % (identifier, e, where))
        raise ValueError(msg)

    # Now let's check the condition
    if isinstance(condition, str):
        # We assume it is a condition that should parse cleanly
        try:
            # could call parse_flexible_spec as well here
            bare_contract = parse_contract_string_actual(condition)
        except ContractSyntaxError as e:
            msg = ('The given condition %r does not parse cleanly: %s' %
                   (condition, e))
            raise ValueError(msg)
    # Important: types are callable, so check this first.
    elif hasattr(condition, '__weakrefoffset__'):
        # parse_flexible_spec can take care of types
        bare_contract = parse_flexible_spec(condition)
    # Lastly, it should be a callable
    elif hasattr(condition, '__call__'):
        # Check that the signature is right
        if can_accept_self(condition):
            bare_contract = CheckCallableWithSelf(condition)
        elif can_accept_at_least_one_argument(condition):
            bare_contract = CheckCallable(condition)
        else:
            raise ValueError("The given callable %r should be able to accept "
                             "at least one argument" % condition)
    else:
        raise ValueError('I need either a string or a callable for the '
                         'condition; found %s.' % describe_value(condition))

    # Separate the context if needed
    if isinstance(bare_contract, (CheckCallable, CheckCallableWithSelf)):
        contract = bare_contract
    else:
        contract = SeparateContext(bare_contract)

    # It's okay if we define the same thing twice
    if identifier in Extension.registrar:
        old = Extension.registrar[identifier]
        if not (contract == old):
            msg = ('Tried to redefine %r with a definition that looks '
                   'different to me.\n' % identifier)
            msg += ' - old: %r\n' % old
            msg += ' - new: %r\n' % contract
            raise ValueError(msg)
    else:
        Extension.registrar[identifier] = contract

    # Before, we check that we can parse it now
    # - not anymore, because since there are possible args/kwargs,
    # - it might be that the keyword alone is not a valid contract
    # if False:
    #     try:
    #         c = parse_contract_string(identifier)
    #         expected = Extension(identifier)
    #         assert c == expected, \
    #             'Expected %r, got %r.' % (c, expected)  # pragma: no cover
    #     except ContractSyntaxError:  # pragma: no cover
    #         #assert False, 'Cannot parse %r: %s' % (identifier, e)
    #         raise

    return contract


def parse_contract_string_actual(string):
    msg: str
    where: Where
    check_param_is_string(string)
    if string in Storage.string2contract:
        return Storage.string2contract[string]
    try:
        c = contract_expression.parseString(string, parseAll=True)[0]
        assert hasattr(c, '__contract__'), 'Want Contract, not %r' % c
        if _cacheable(string, c):
            Storage.string2contract[string] = c
        return c
    except Exception as e:
        msg = '%s' % e
        if hasattr(e, 'loc'):  # ParseBaseException
            where = Where(string, character=e.loc)
            raise ContractSyntaxError(msg, where=where)
        else:
            raise  # ContractDefinitionError


def check_contracts(contracts, values, context_variables=None):
    """
        Checks that the values respect the contract.
        Not a public function -- no friendly messages.

        :param contracts: List of contracts.
        :type contracts:  ``list[N](str),N>0``

        :param values: Values that should match the contracts.
        :type values: ``list[N]``

        :param context_variables: Initial context
        :type context_variables: ``dict(str[1]: *)``

        :return: a Context variable
        :rtype: type(Context)

        :raise: ContractSyntaxError
        :raise: ContractNotRespected
        :raise: ValueError
    """
    assert isinstance(contracts, list)
    assert isinstance(contracts, list)
    assert len(contracts) == len(values)

    if context_variables is None:
        context_variables = {}

    for var in context_variables:
        if not (isinstance(var, str) and len(var) == 1):  # XXX: isalpha
            msg = ('Invalid name %r for a variable. '
                   'I expect a string of length 1.' % var)
            raise ValueError(msg)

    C = []
    for x in contracts:
        assert isinstance(x, str)
        C.append(parse_contract_string_actual(x))

    context = context_variables.copy()
    for i in range(len(contracts)):
        C[i]._check_contract(context, values[i], silent=False)

    return context
