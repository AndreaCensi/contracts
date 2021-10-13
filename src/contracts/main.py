import sys
from typing import Callable, cast, TypeVar, Any, Type
from ._compat import IS_PY2, basestring
from inspect import getfullargspec
from ._compat import IS_PY3A_OR_GREATER
from .inspection import getcallargs
from .docstring_parsing import Arg, DocStringInfo
from .interface import (CannotDecorateClassmethods, Contract,
    ContractDefinitionError, ContractException, ContractNotRespected,
    ContractSyntaxError, MissingContract, describe_value)
from .main_actual import parse_contract_string_actual, check_contracts, get_all_arg_names
from .library import CheckType


def check(contract, objekt, desc=None, **context):  # must stay in main.py so that contracts can inspect their scope
    """
        Checks that ``object`` satisfies the contract
        described by ``contract``.

        :param contract: The contract string.
        :type contract:  str

        :param objekt: Any object.
        :type objekt: ``*``

        :param desc: An optional description of the error. If given,
                     it is included in the error message.
        :type desc: ``None|str``
    """
    if not isinstance(contract, str):
        # XXX: make it more liberal?
        raise ValueError('I expect a string (contract spec) as the first '
                         'argument, not a %s.' % describe_value(contract))
    try:
        return check_contracts([contract], [objekt], context)
    except ContractNotRespected as e:
        if desc is not None:
            e.error = '%s\n%s' % (desc, e.error)
        raise e


def fail(contract, value, **initial_context):  # must stay in main.py so that contracts can inspect their scope
    """ Checks that the value **does not** respect this contract.
        Raises an exception if it does.

       :raise: ValueError
    """
    try:
        parsed_contract = parse_contract_string_actual(contract)
        context = check_contracts([contract], [value], initial_context)
    except ContractNotRespected:
        pass
    else:
        msg = 'I did not expect that this value would satisfy this contract.\n'
        msg += '-    value: %s\n' % describe_value(value)
        msg += '- contract: %s\n' % parsed_contract
        msg += '-  context: %r' % context
        raise ValueError(msg)


def check_multiple(couples, desc=None):  # must stay in main.py so that contracts can inspect their scope
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

    check('list[>0](tuple(str, *))', couples, 'I expect a non-empty list of (object, string) tuples.')
    contracts = [x[0] for x in couples]
    values = [x[1] for x in couples]
    try:
        return check_contracts(contracts, values)
    except ContractNotRespected as e:
        if desc is not None:
            e.error = '%s\n%s' % (desc, e.error)
        raise e


# if IS_PY3A_OR_GREATER:  # Python 3.10: Essentially the same level of optimization as below but much more pythonic
#     def parse_flexible_spec(spec):
#         match spec:
#             case Contract():
#                 return spec
#             case type():
#                 return CheckType(spec)
#             case str():
#                 return parse_contract_string_actual(spec)
#             case _:
#                 msg = 'I want either a string or a type, not %s.' % describe_value(spec)
#                 raise ContractException(msg)
# else:
def parse_flexible_spec(spec):  # must stay in main.py so that contracts can inspect their scope
    """ spec can be either a Contract, a type, or a contract string.
        In the latter case, the usual parsing takes place"""
    if hasattr(spec, '__contract__'):  # isinstance(spec, Contract) substitute using the __contract__ slot
        return spec
    elif hasattr(spec, '__weakrefoffset__'):  # isinstance(spec, type)
        return CheckType(spec)
    elif isinstance(spec, str):
        return parse_contract_string_actual(spec)
    else:
        msg = 'I want either a string or a type, not %s.' % describe_value(spec)
        raise ContractException(msg)


F = TypeVar('F', bound=Callable[..., Any])


def contract_decorator(*arg, **kwargs) -> F:
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
        if isinstance(arg[0], Callable):
            # We were called without parameters
            function = arg[0]
            try:
                return cast(F, contracts_decorate(function, **kwargs))
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
        def tmp_wrap(f: F) -> F:  # do not change name (see above)
            try:
                return contracts_decorate(f, **kwargs)
            except ContractSyntaxError as e:
                msg = u"Cannot decorate function %s:" % f.__name__
                from .utils import indent
                import traceback
                msg += u'\n\n' + indent(traceback.format_exc(), u'  ')
                raise ContractSyntaxError(msg, e.where)
                # erase the stack
            except ContractDefinitionError as e:
                raise e.copy()
                # raise

        return cast(F, tmp_wrap)


def contracts_decorate(function_: F, modify_docstring=True, **kwargs) -> F:
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
        annotations = getfullargspec(function_).annotations

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

        return cast(F, result)

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
    name = ('checker-for-%s' % function_.__name__)
    if IS_PY2:  # pragma: no cover
        name = name.encode('utf-8')
    contracts_checker.__name__ = name
    contracts_checker.__module__ = function_.__module__

    # TODO: is using functools.wraps better than decorator.decorate?
    from ..decorator import decorate

    wrapper = decorate(function_, contracts_checker)

    wrapper.__doc__ = new_docs
    wrapper.__name__ = function_.__name__
    wrapper.__module__ = function_.__module__

    wrapper.__contracts__ = dict(returns=returns_parsed, **accepts_parsed)
    return cast(F, wrapper)


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

    return name2type, returns


inPy3k = sys.version_info[0] == 3


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
    from .main_actual import new_contract_impl
    if args and len(args) == 1 and isinstance(args[0], Callable):
        # TODO: add class decorator for new_contract
        # We were called without parameters
        function = args[0]
        identifier = function.__name__
        new_contract_impl(identifier, function)
        return function
    else:
        return new_contract_impl(*args)


def parse_contract_string(string):
    return parse_contract_string_actual(string)

