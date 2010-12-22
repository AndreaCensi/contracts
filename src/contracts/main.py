import types
import inspect

from .syntax import contract, ParseException
from .interface import (Context, Contract, ContractSyntaxError, Where,
                        ContractException, ContractNotRespected)
from .docstring_parsing import parse_docstring_annotations
from contracts.backported import getcallargs
from contracts.interface import describe_value

def check_contracts(contracts, values):
    ''' 
        Checks that the values respect the contract. 
        Not a public function -- no friendly messages.
        
        :param contracts: List of contracts.
        :type contracts:  list[N](str),N>0
        
        :param values: Values that should match the contracts.
        :type values: list[N]
    
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
    
# TODO: add decorator-specific exception

def contracts(accepts=None, returns=None):
    ''' Decorator for turning functions into simple blocks. '''        
    # OK, this is black magic. You are not expected to understand this.
    if type(accepts) is types.FunctionType:
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
    ''' An explicit way to decorate a given function. '''
    args, varargs, varkw, defaults = inspect.getargspec(function) #@UnusedVariable

    all_args = filter(None, args + [varargs, varkw])

#    if varargs is not None:
#        raise ContractException('Sorry! contracts does not work with varargs.')
#    if varkw is not None:
#        raise ContractException('Sorry! contracts does not work with kwargs.')
    
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
        
#        if len(pargs) != len(args):
#            raise ContractNotRespected('This function accepts %d parameters, '
#                                       'not %d.' % (len(args), len(pargs)))

        context = Context()
        for arg in all_args:
            if arg in accepts_parsed:
                accepts_parsed[arg]._check_contract(context, bound[arg])
        
        #print('Arguments %r passed %r.' % (pargs, accepts_parsed))    
        result = function(*args, **kwargs)
        
        returns_parsed._check_contract(context, result)
        
        #print(' return %r passed %r.' % (pargs, accepts_parsed))
        
        return result
    
    wrapper.__doc__ = function.__doc__
    # TODO: create a docstring from specified accepts/returns if one is missing?
    return wrapper


def parse_contracts_from_docstring(function):
    #try:
    # FIXME: Note: this never fails; at best it ignores unclosed things. 
    annotations = parse_docstring_annotations(function.__doc__)
    #except Exception as e:
    #    raise ContractException('Could not parse docstring: %s' % e)
    
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
    all_args = filter(None, args + [varargs, varkw])
    
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
    
        :type contract: str
        
        :param desc: An optional description of the error. If given, 
                     it is included in the error message.
        :type desc: None|str
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


def new_contract(identifier, contract):
    ''' Defines a new contract type. The second parameter can be either
        a string or a callable function. 
        
        - If it is a string, it is interpreted as contract expression; 
          the given identifier will become an alias
          for that expression. 
          
        - If it is a callable, it must accept one parameter, and return 
          either True or False. 
    
        :param identifier: The identifier must be a string not already in use
                          (you cannot redefine ``list``, ``tuple``, etc.).
        :type identifier: str 
        
        :param contract: Definition of the new contract.
        :type contract: callable|str
        
    '''
    pass
    
    
    