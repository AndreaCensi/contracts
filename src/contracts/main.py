import sys
import types

import six

from .backported import getcallargs, getfullargspec
from .docstring_parsing import Arg, DocStringInfo
from .enabling import all_disabled
from .inspection import (can_accept_at_least_one_argument, can_accept_self,
    can_be_used_as_a_type)
from .interface import (CannotDecorateClassmethods, Contract,
    ContractDefinitionError, ContractException, ContractNotRespected,
    ContractSyntaxError, MissingContract, Where, describe_value)


# from .library import (CheckCallable, Extension, SeparateContext,
#     identifier_expression)
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
        C.append(parse_contract_string(x))

    context = context_variables.copy()
    for i in range(len(contracts)):
        C[i]._check_contract(context, values[i], silent=False)

    return context


class Storage:
    # Cache storage
    string2contract = {}


def _cacheable(string, c):
    """ Returns whether the contract c defined by string string is cacheable. """
    # XXX need a more general way of indicating
    #     whether a contract is safely cacheable
    return '$' not in string


def is_param_string(x):
    return isinstance(x, six.string_types)


def check_param_is_string(x):
    if not is_param_string(x):
        msg = 'Expected a string, obtained %s' % type(x)
        raise ValueError(msg)

# TODO: add decorator-specific exception


def contract_decorator(*arg, **kwargs):
    """
        Decorator for adding contracts to functions.

        It is smart enough to support functions with variable number of
        arguments and keyword arguments.

        There are three ways to specify the contracts. In order of precedence:

        - As arguments to this decorator. For example: ::

              @contract(a='int,>0',b='list[N],N>0',returns='list[N]')
              def my_function(a, b):
                  # ...
                  pass

        - As annotations (supported only in Python 3): ::

              @contract
              def my_function(a:'int,>0', b:'list[N],N>0') -> 'list[N]':
                  # ...
                  pass

        - Using ``:type:`` and ``:rtype:`` tags in the function's docstring: ::

              @contract
              def my_function(a, b):
                  """
    # OK, this is black magic. You are not expected to understand this.
    if arg:
        if isinstance(arg[0], types.FunctionType):
            # We were called without parameters
            function = arg[0]
            if all_disabled():
                return function
            try:
                return contracts_decorate(function, **kwargs)
            except ContractSyntaxError as es:
                # Erase the stack
                raise ContractSyntaxError(es.error, es.where)
        else:
            msg = ('I expect that contracts() is called with '
                   'only keyword arguments (passed: %r)' % arg)
            raise ContractException(msg)
    else:
        # !!! Do not change "tmp_wrap" name; we need it for the definition
        # of scoped variable

        # We were called *with* parameters.
        if all_disabled():

            def tmp_wrap(f):  # do not change name (see above)
                return f

        else:

            def tmp_wrap(f):  # do not change name (see above)
                try:
                    return contracts_decorate(f, **kwargs)
                except ContractDefinitionError as e:
                    # erase the stack
                    raise e.copy()

        return tmp_wrap


def contracts_decorate(function_, modify_docstring=True, **kwargs):
    """ An explicit way to decorate a given function.
        The decorator :py:func:`decorate` calls this function internally.
    """

    if isinstance(function_, classmethod):
        msg = """
The function is a classmethod; PyContracts cannot decorate a classmethod.
You can, however, first decorate a function and then turn it into a
classmethod.

For example, instead of doing this:

    class A():

        @contract(a='>0')
        @classmethod
        def f(cls, a):
            pass

you can achieve the same goal by inverting the two decorators:

    class A():

        @classmethod
        @contract(a='>0')
        def f(cls, a):
            pass
"""
        raise CannotDecorateClassmethods(msg)

    all_args = get_all_arg_names(function_)

    if kwargs:

        returns = kwargs.pop('returns', None)

        for kw in kwargs:
            if not kw in all_args:
                msg = 'Unknown parameter %r; I know %r.' % (kw, all_args)
                raise ContractException(msg)

        accepts_dict = dict(**kwargs)

    else:
        # Py3k: check if there are annotations
        annotations = get_annotations(function_)

        if annotations:
            if 'return' in annotations:
                returns = annotations['return']
                del annotations['return']
            else:
                returns = None

            accepts_dict = annotations
        else:
            # Last resort: get types from documentation string.
            if function_.__doc__ is None:
                # XXX: change name
                raise ContractException(
                    'You did not specify a contract, nor I can '
                    'find a docstring for %r.' % function_)

            accepts_dict, returns = parse_contracts_from_docstring(function_)

            if not accepts_dict and not returns:
                raise ContractException('No contract specified in docstring.')

    if returns is None:
        returns_parsed = None
    else:
        returns_parsed = parse_flexible_spec(returns)

    accepts_parsed = dict([(x, parse_flexible_spec(accepts_dict[x]))
                           for x in accepts_dict])

    is_bound_method = 'self' in all_args

    def contracts_checker(unused, *args, **kwargs):
        do_checks = not all_disabled()
        if not do_checks:
            return function_(*args, **kwargs)

        def get_nice_function_display():
            nice_function_display = '%s()' % function_.__name__
            if is_bound_method:
                klass = type(args[0]).__name__
                nice_function_display = klass + ':' + nice_function_display
            return nice_function_display

        bound = getcallargs(function_, *args, **kwargs)

        context = {}
        # add self if we are a bound method
        if is_bound_method:
            context['self'] = args[0]

        for arg in all_args:
            if arg in accepts_parsed:
                try:
                    accepts_parsed[arg]._check_contract(context, bound[arg], silent=False)
                except ContractNotRespected as e:
                    msg = ('Breach for argument %r to %s.\n'
                           % (arg, get_nice_function_display()))
                    e.error = msg + e.error
                    raise e

        result = function_(*args, **kwargs)

        if returns_parsed is not None:
            try:
                returns_parsed._check_contract(context, result, silent=False)
            except ContractNotRespected as e:
                msg = ('Breach for return value of %s.\n'
                       % (get_nice_function_display()))
                e.error = msg + e.error
                raise e

        return result

    # TODO: add rtype statements if missing

    if modify_docstring:

        def write_contract_as_rst(c):
            return '``%s``' % c

        if function_.__doc__ is not None:
            docs = DocStringInfo.parse(function_.__doc__)
        else:
            docs = DocStringInfo("")
        for param in accepts_parsed:
            if not param in docs.params:
                # default = '*not documented*'
                default = ''
                docs.params[param] = Arg(default, None)

            docs.params[param].type = \
                write_contract_as_rst(accepts_parsed[param])

        if returns_parsed is not None:
            if not docs.returns:
                docs.returns.append(Arg(None, None))
            docs.returns[0].type = write_contract_as_rst(returns_parsed)
        new_docs = docs.__str__()

    else:
        new_docs = function_.__doc__

    # XXX: why doesn't this work?
    contracts_checker.__name__ = 'checker-for-%s' % function_.__name__
    contracts_checker.__module__ = function_.__module__

    # TODO: is using functools.wraps better?
    from decorator import decorator  # @UnresolvedImport

    wrapper = decorator(contracts_checker, function_)

    wrapper.__doc__ = new_docs
    wrapper.__name__ = function_.__name__
    wrapper.__module__ = function_.__module__

    wrapper.__contracts__ = dict(returns=returns_parsed, **accepts_parsed)
    return wrapper


def parse_flexible_spec(spec):
    """ spec can be either a Contract, a type, or a contract string.
        In the latter case, the usual parsing takes place"""
    if isinstance(spec, Contract):
        return spec
    elif is_param_string(spec):
        return parse_contract_string(spec)
    elif can_be_used_as_a_type(spec):
        from .library import CheckType
        return CheckType(spec)
    else:
        msg = 'I want either a string or a type, not %s.' % describe_value(spec)
        raise ContractException(msg)


def parse_contracts_from_docstring(function):
    annotations = DocStringInfo.parse(function.__doc__)

    if len(annotations.returns) > 1:
        raise ContractException('More than one return type specified.')

    def remove_quotes(x):
        """ Removes the double back-tick quotes if present. """
        if x is None:
            return None
        if x.startswith('``') and x.endswith('``') and len(x) > 3:
            return x[2:-2]
        elif x.startswith('``') or x.endswith('``'):
            msg = 'Malformed quoting in string %r.' % x
            raise ContractException(msg)
        else:
            return x

    if len(annotations.returns) == 0:
        returns = None
    else:
        returns = remove_quotes(annotations.returns[0].type)

    # These are the annotations
    params = annotations.params
    name2type = dict([(name, remove_quotes(params[name].type))
                      for name in params])

    # Check the ones that do not have contracts specified
    nullparams = [name for name in params if params[name].type is None]
    if nullparams:
        msg = ('The parameter(s) %r in this docstring have no type statement.'
               % (",".join(nullparams)))
        msg += """

Note: you can use the asterisk if you do not care about assigning
a contract to a certain parameter:

    :param x:
    :type x: *
"""
        raise MissingContract(msg)

    # Let's look at the parameters:
    all_args = get_all_arg_names(function)

    # Check we don't have extra:
    for name in name2type:
        if not name in all_args:
            msg = ('A contract was specified for argument %r which I cannot'
                   ' find in my list of arguments (%r)' %
                   (name, all_args))
            raise ContractException(msg)

    if len(name2type) != len(all_args):  # pragma: no cover
        pass
        # TODO: warn?

    return name2type, returns


inPy3k = sys.version_info[0] == 3


def get_annotations(function):
    return getfullargspec(function).annotations


def get_all_arg_names(function):
    spec = getfullargspec(function)
    possible = spec.args + [spec.varargs, spec.varkw] + spec.kwonlyargs
    all_args = [x for x in possible if x]
    return all_args


def check(contract, object, desc=None, **context):  # @ReservedAssignment
    """
        Checks that ``object`` satisfies the contract
        described by ``contract``.

        :param contract: The contract string.
        :type contract:  str

        :param object: Any object.
        :type object: ``*``

        :param desc: An optional description of the error. If given,
                     it is included in the error message.
        :type desc: ``None|str``
    """
    if all_disabled():
        return {}

    if not is_param_string(contract):
        # XXX: make it more liberal?
        raise ValueError('I expect a string (contract spec) as the first '
                         'argument, not a %s.' % describe_value(contract))
    try:
        return check_contracts([contract], [object], context)
    except ContractNotRespected as e:
        if desc is not None:
            e.error = '%s\n%s' % (desc, e.error)
        raise e


def fail(contract, value, **initial_context):
    """ Checks that the value **does not** respect this contract.
        Raises an exception if it does.

       :raise: ValueError
    """
    try:
        parsed_contract = parse_contract_string(contract)
        context = check_contracts([contract], [value], initial_context)
    except ContractNotRespected:
        pass
    else:
        msg = 'I did not expect that this value would satisfy this contract.\n'
        msg += '-    value: %s\n' % describe_value(value)
        msg += '- contract: %s\n' % parsed_contract
        msg += '-  context: %r' % context
        raise ValueError(msg)


def check_multiple(couples, desc=None):
    """
        Checks multiple couples of (contract, value) in the same context.

        This means that the variables in each contract are shared with
        the others.

        :param couples: A list of tuple (contract, value) to check.
        :type couples: ``list[>0](tuple(str, *))``

        :param desc: An optional description of the error. If given,
                     it is included in the error message.
        :type desc: ``None|str``
    """

    check('list[>0](tuple(str, *))', couples,
          'I expect a non-empty list of (object, string) tuples.')
    contracts = [x[0] for x in couples]
    values = [x[1] for x in couples]
    try:
        return check_contracts(contracts, values)
    except ContractNotRespected as e:
        if desc is not None:
            e.error = '%s\n%s' % (desc, e.error)
        raise e


def new_contract(*args):
    """ Defines a new contract type. Used both as a decorator and as
        a function.

        **1) Use as a function.** The first parameter must be a string.
        The second parameter can be either
        a string or a callable function.  ::

            new_contract('new_contract_name', 'list[N]')
            new_contract('new_contract_name', lambda x: isinstance(x, list) )

        - If it is a string, it is interpreted as contract expression;
          the given identifier will become an alias
          for that expression.

        - If it is a callable, it must accept one parameter, and either:

          * return True or None, to signify it accepts.

          * return False or raise ValueError or AssertionError,
            to signify it doesn't.

          If ValueError is raised, its message is used in the error.

        **2) Use as a decorator.**

        Or, it can be used as a decorator (without arguments).
        The function name is used as the identifier. ::

            @new_contract
            def new_contract_name(x):
                return isinstance(x, list)


        This function returns a :py:class:`Contract` object. It might be
        useful to check right away if the declaration is what you meant,
        using :py:func:`Contract.check` and :py:func:`Contract.fail`.

        :param identifier: The identifier must be a string not already in use
                          (you cannot redefine ``list``, ``tuple``, etc.).
        :type identifier: str

        :param condition: Definition of the new contract.
        :type condition: ``type|callable|str``

        :return: The equivalent contract -- might be useful for debugging.
        :rtype: Contract
    """
    if args and len(args) == 1 and isinstance(args[0], types.FunctionType):
        # TODO: add here for class decorator
        # We were called without parameters
        function = args[0]
        if all_disabled():
            return function
        identifier = function.__name__
        new_contract_impl(identifier, function)
        return function
    else:
        if all_disabled():
            return None  # XXX: not really sure about this
        return new_contract_impl(*args)


def new_contract_impl(identifier, condition):

    from .syntax import ParseException
    from .library.extensions import CheckCallableWithSelf
    from .library import (CheckCallable, Extension, SeparateContext,
        identifier_expression)

    # Be friendly
    if not isinstance(identifier, str):
        raise ValueError('I expect the identifier to be a string; '
                         'received %s.' %
                         describe_value(identifier))

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
            c = parse_contract_string(identifier)
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
        where = Where(identifier, character=loc)  #line=e.lineno, column=e.col)
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
            bare_contract = parse_contract_string(condition)
        except ContractSyntaxError as e:
            msg = ('The given condition %r does not parse cleanly: %s' %
                   (condition, e))
            raise ValueError(msg)
    # Important: types are callable, so check this first.
    elif can_be_used_as_a_type(condition):
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
    if False:
        try:
            c = parse_contract_string(identifier)
            expected = Extension(identifier)
            assert c == expected, \
                'Expected %r, got %r.' % (c, expected)  # pragma: no cover
        except ContractSyntaxError as e:  # pragma: no cover
            #assert False, 'Cannot parse %r: %s' % (identifier, e)
            raise e

    return contract


def parse_contract_string(string):
    from .main_actual import parse_contract_string_actual
    return parse_contract_string_actual(string)

