import types
import inspect

from .syntax import contract, ParseException, ParseFatalException
from .interface import (Context, Contract, ContractSyntaxError, Where,
                        ContractException, ContractNotRespected, describe_value)
from .docstring_parsing import parse_docstring_annotations
from .backported import getcallargs
from .library import (identifier_expression, Extension,
                      CheckCallable, SeparateContext) 


def check_contracts(contracts, values):
    ''' 
        Checks that the values respect the contract. 
        Not a public function -- no friendly messages.
        
        :param contracts: List of contracts.
        :type contracts:  ``list[N](str),N>0``
        
        :param values: Values that should match the contracts.
        :type values: ``list[N]``
    
        :return: a Context variable 
        :rtype: type(Context)
        
        :raise: ContractSyntaxError
        :raise: ContractNotRespected
        :raise: ValueError
    '''
    assert isinstance(contracts, list)
    assert isinstance(contracts, list)
    assert len(contracts) == len(values)
    
    C = []
    for x in contracts:
        assert isinstance(x, str)
        C.append(parse_contract_string(x))

    context = Context()
    for i in range(len(contracts)):
        C[i]._check_contract(context, values[i])
    
    return context

class Storage:
    string2contract = {}

def parse_contract_string(string, filename=None):
    assert isinstance(string, str), type(string)
    if string in Storage.string2contract:
        return Storage.string2contract[string]
    try:
        c = contract.parseString(string, parseAll=True)[0] 
        assert isinstance(c, Contract), 'Want Contract, not %r' % c
        Storage.string2contract[string] = c
        return c
    except ParseException as e:
        where = Where(filename, string, line=e.lineno, column=e.col)
        msg = 'Error in parsing string: %s' % e
        raise ContractSyntaxError(msg, where=where)
    except ParseFatalException as e:
        where = Where(filename, string, line=e.lineno, column=e.col)
        msg = 'Error in parsing string: %s' % e
        raise ContractSyntaxError(msg, where=where)
    
# TODO: add decorator-specific exception

def contracts(accepts=None, returns=None):
    ''' Decorator for adding contracts check of arguments and return values.
    
        It is smart enough to support functions with variable number of arguments
        and keyword arguments.
        
        - If neither ``accepts`` or ``returns`` is passed, the contracts
          are read from the function's docstring, using the ``rtype`` and 
          ``:type:`` tags.   
          
          Note that, by convention, those annotations must be parseable as
          RestructuredText. This is relevant if you are using Sphinx.
          If the contract string has special RST characters in it, like ``*``,
          you can include it in double ticks. |pycontracts| will remove
          the double ticks before interpreting the string.
          
          For example, the two annotations in this docstring are equivalent
          for |pycontracts|, but the latter is better for Sphinx: ::
          
              """ My function 
              
                  :param a: First parameter
                  :type a: list(tuple(str,*))
                  
                  :param b: First parameter
                  :type b: ``list(tuple(str,*))``
              """
    
        - If ``accepts`` is passed, it must be a list of strings specifying
          the contracts for the argument (in order).
          
        - If ``returns`` is passed, it must be a string, indicating the
          contract for the return value. It is evaluated in the same context
          as the contracts in ``accepts``. 
        
        :raise: ContractException, if arguments are not coherent with the function
        :raise: ContractSyntaxError
    '''        
    # OK, this is black magic. You are not expected to understand this.
    if isinstance(accepts, types.FunctionType):
        # We were called without parameters
        function = accepts
        accepts = None
        returns = None
        return contracts_decorate(function, accepts, returns)
    else:
        # We were called *with* parameters.
        def wrap(function):
            return contracts_decorate(function, accepts, returns)
        return wrap

def contracts_decorate(function, accepts=None, returns=None):
    ''' An explicit way to decorate a given function.
        The decorator :py:func:`decorate` calls this function internally. 
    '''
    args, varargs, varkw, defaults = inspect.getargspec(function) #@UnusedVariable
    all_args = [x for x in  args + [varargs, varkw] if x]

    if accepts is None and returns is None:
        # Get types from documentation string.
        if function.__doc__ is None:
            # XXX: change name
            raise ContractException('You did not specify a contract, nor I can '
                                    'find a docstring for %r.' % function)
        
        accepts_dict, returns = parse_contracts_from_docstring(function)
        
        if not accepts_dict and not returns:
            raise ContractException('No contract specified in docstring.')
    else: 
        if len(accepts) > len(all_args):
            raise ContractException('Found  %d specs for %d arguments.' % 
                                    (len(accepts), len(args)))
        
        accepts_dict = {}
        for i in range(len(accepts)):
            accepts_dict[all_args[i]] = accepts[i] 
    
    if returns is None:
        returns = '*'
        
    accepts_parsed = dict([ (x, parse_contract_string(accepts_dict[x])) 
                            for x in accepts_dict])
    returns_parsed = parse_contract_string(returns)
    
    # I like this meta-meta stuff :-)
    def wrapper(*args, **kwargs):
        bound = getcallargs(function, *args, **kwargs)
        
        context = Context()
        for arg in all_args:
            if arg in accepts_parsed:
                accepts_parsed[arg]._check_contract(context, bound[arg])
        
        result = function(*args, **kwargs)
        
        returns_parsed._check_contract(context, result)
        
        return result
    
    wrapper.__doc__ = function.__doc__
    
    return wrapper


def parse_contracts_from_docstring(function):
    annotations = parse_docstring_annotations(function.__doc__)
    
    if len(annotations.returns) > 1:
        raise ContractException('More than one return type specified.')
    
    def remove_quotes(x):
        ''' Removes the double back-tick quotes if present. '''
        if x.startswith('``') and x.endswith('``') and len(x) > 3:
            return x[2:-2]
        else:
            return x
    
    if len(annotations.returns) == 0:
        returns = None
    else:
        returns = remove_quotes(annotations.returns[0].type)
        
    # These are the annotations
    params = annotations.params
    name2type = dict([ (name, remove_quotes(params[name].type)) 
                       for name in params])
    
    # Let's look at the parameters:
    args, varargs, varkw, defaults = inspect.getargspec(function) #@UnusedVariable
    all_args = [x for x in  args + [varargs, varkw] if x]
    
    # Check we don't have extra:
    for name in name2type:
        if not name in all_args:
            msg = ('A contract was specified for argument %r which I cannot find'
                   ' in my list of arguments (%s)' % (name, ", ".join(all_args)))
            raise ContractException(msg)
        
    if len(name2type) != len(all_args): # pragma: no cover
        pass
        # TODO: warn?
        # msg = 'Found %d contracts for %d variables.' % (len(name2type), len(args))
        
    return name2type, returns


def check(contract, object, desc=None):
    ''' 
        Checks that ``object`` satisfies the contract described by ``contract``.
    
        :param contract: The contract string.
        :type contract:  str
        
        :param object: Any object.
        :type object: ``*``

        :param desc: An optional description of the error. If given, 
                     it is included in the error message.
        :type desc: ``None|str``
    '''
    if not isinstance(contract, str):
        raise ValueError('I expect a string (contract spec) as the first '
                         'argument, not a %s.' % contract.__class__)
    try:
        return check_contracts([contract], [object])
    except ContractNotRespected as e:
        if desc is not None:
            e.error = '%s\nDetails of PyContracts error:\n%s' % (desc, e.error)
        raise


def check_multiple(couples, desc=None):
    ''' 
        Checks multiple couples of (contract, value) in the same context. 
        
        This means that the variables in each contract are shared with 
        the others. 
        
        :param couples: A list of tuple (contract, value) to check.
        :type couples: ``list[>0](tuple(str, *))``
        
        :param desc: An optional description of the error. If given, 
                     it is included in the error message.
        :type desc: ``None|str``
    ''' 
    
    check('list[>0](tuple(str, *))', couples,
          'I expect a non-empty list of (object, string) tuples.')
    contracts = [x[0] for x in couples]
    values = [x[1] for x in couples]
    try:
        return check_contracts(contracts, values)
    except ContractNotRespected as e:
        if desc is not None:
            e.error = '%s\n\nDetails:\n%s' % (desc, e.error)
        raise    


def new_contract(identifier, condition):
    ''' Defines a new contract type. The second parameter can be either
        a string or a callable function. 
        
        - If it is a string, it is interpreted as contract expression; 
          the given identifier will become an alias
          for that expression. 
          
        - If it is a callable, it must accept one parameter, and either:
          
          * return True or None, to signify it accepts.
          
          * return False or raise ValueError, to signify it doesn't.
          
          If ValueError is raised, its message is used in the error.
          
        This function returns a :py:class:`Contract` object. It might be
        useful to check right away if the declaration is what you meant,
        using :py:func:`Contract.check` and :py:func:`Contract.fail`.  
        
        :param identifier: The identifier must be a string not already in use
                          (you cannot redefine ``list``, ``tuple``, etc.).
        :type identifier: str 
        
        :param condition: Definition of the new contract.
        :type condition: ``callable|str``
        
        :return: The equivalent contract -- might be useful for debugging.
        :rtype: Contract
    '''
    
    # Be friendly
    if not isinstance(identifier, str):
        raise ValueError('I expect the identifier to be a string; received %s.' % 
                         describe_value(identifier))
    
    # Make sure it is not already an expression that we know.
    #  (exception: allow redundant definitions. To this purpose,
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
            raise ValueError('Invalid identifier %r; it overwrites an already known '
                             'expression. In fact, I can parse it as %s (%r).' % 
                             (identifier, c, c))
        except ContractSyntaxError:
            pass
        
    # Make sure it corresponds to our idea of identifier
    try:
        c = identifier_expression.parseString(identifier, parseAll=True)
    except ParseException as e:
        where = Where(None, identifier, line=e.lineno, column=e.col)
        #msg = 'Error in parsing string: %s' % e    
        raise ValueError('The given identifier %r does not correspond to my idea '
                         'of what an identifier should look like;\n%s\n%s' 
                         % (identifier, e, where))
    
    # Now let's check the condition
    if isinstance(condition, str):
        # We assume it is a condition that should parse cleanly
        try:
            bare_contract = parse_contract_string(condition)
        except ContractSyntaxError as e:
            raise ValueError('The given condition %r does not parse cleanly: %s' % 
                             (condition, e))
    elif hasattr(condition, '__call__'):
        # Check that the signature is right
        if not can_accept_exactly_one_argument(condition):
            raise ValueError('The given callable %r should be able to accept '
                             'exactly one argument.' % condition)
        bare_contract = CheckCallable(condition)
    else:
        raise ValueError('I need either a string or a callable for the '
                         'condition; found %s.' % describe_value(condition))
    
    # Separate the context
    contract = SeparateContext(bare_contract)
    
    # It's okay if we define the same thing twice
    if identifier in Extension.registrar:
        old = Extension.registrar[identifier]
        if not(contract == old):
            msg = ('Tried to redefine %r with a definition that looks '
                   'different to me.\n' % identifier)
            msg += ' - old: %r\n' % old
            msg += ' - new: %r\n' % contract
            raise ValueError(msg)
    else:
        Extension.registrar[identifier] = contract
        
    # Check that we can parse it now
    try:
        c = parse_contract_string(identifier)
        expected = Extension(identifier)
        assert c == expected, \
              'Expected %r, got %r.' % (c, expected) # pragma: no cover
    except ContractSyntaxError as e: # pragma: no cover
        assert False, 'Cannot parse %r: %s' % (identifier, e)
        
    return bare_contract

def can_accept_exactly_one_argument(callable_thing):
    ''' Checks that a callable can accept exactly one argument
        using introspection.
    '''
    if inspect.ismethod(callable_thing): # bound method
        f = callable_thing.__func__
        args = (callable_thing.__self__, 'test',)
    else:
        if not inspect.isfunction(callable_thing):
            f = callable_thing.__call__
        else:
            f = callable_thing
        args = ('test',)
    
    try:
        getcallargs(f, *args)
    except (TypeError, ValueError) as e: #@UnusedVariable
        # print 'Get call args exception (f=%r,args=%r): %s ' % (f, args, e)
        return False
    else:
        return True
    
    
