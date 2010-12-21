import types
import inspect

from .syntax import contract, ParseException
from .interface import (Context, Contract, ContractSyntaxError, Where,
                        ContractException, ContractNotRespected)
from .docstring_parsing import parse_docstring_annotations

def check_contracts(contracts, values):
    ''' 
        Checks that the values respect the contract. 
        
        :param contracts: List of contracts.
        :type contracts:  list[N](str),N>0
        
        :param values: Values that should match the contracts.
        :type values: list[N]
    
        :return: a Context variable 
        :rtype: type(Context)
        
        :raise: ContractError
    '''
    assert isinstance(contracts, list)
    assert isinstance(contracts, list)
    assert len(contracts) == len(values)
    
    C = []
    for x in contracts:
        if not isinstance(x, str):
            raise ValueError('I expect arguments to be strings, not %r.' % type(x))
        C.append(parse_contract_string(x))

    context = Context()
    for i in range(len(contracts)):
        C[i]._check_contract(context, values[i])
        # print '%s  %r  (%s) ' % (C[i], C[i], C[i].__class__)
    
    return context

class Storage:
    string2contract = {}

def parse_contract_string(string, filename=None):
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
    args, varargs, varkw, defaults = inspect.getargspec(function) #@UnusedVariable

    if varargs is not None:
        raise ContractException('Sorry! contracts does not work with varargs.')
    if varkw is not None:
        raise ContractException('Sorry! contracts does not work with kwargs.')
    
    if accepts is None and returns is None:
        # Get types from documentation string.
        if function.__doc__ is None:
            raise ContractException('You did not specify a contract, nor I can '
                                    'find a docstring for %r.' % function)
        
        accepts, returns = parse_contracts_from_docstring(function)
        
        if not accepts and not returns:
            raise ContractException('No contract specified in docstring.')
    else:
    
        if len(accepts) != len(args):
            raise ContractException('Found only %d specs for %d parameters.' % 
                            (len(accepts), len(args)))
    
    if returns is None:
        returns = '*'
        
    accepts_parsed = [parse_contract_string(x) for x in accepts]
    returns_parsed = parse_contract_string(returns)
    
    def wrapper(*pargs):
        if len(pargs) != len(args):
            raise ContractNotRespected('This function accepts %d parameters, '
                                       'not %d.' % (len(args), len(pargs)))
        context = Context()
        for i in range(len(pargs)):
            accepts_parsed[i]._check_contract(context, pargs[i])
        
        #print('Arguments %r passed %r.' % (pargs, accepts_parsed))    
        result = function(*pargs)
        
        returns_parsed._check_contract(context, result)
        
        #print(' return %r passed %r.' % (pargs, accepts_parsed))
        
        return result
    
    wrapper.__doc__ = function.__doc__
    # TODO: create a docstring from specified accepts/returns if one is missing?
    return wrapper


def parse_contracts_from_docstring(function):
    try:
        annotations = parse_docstring_annotations(function.__doc__)
    except Exception as e:
        raise ContractException('Could not parse docstring: %s' % e)
    
    if len(annotations.returns) > 1:
        raise ContractException('More than one return type specified.')
    
    if len(annotations.returns) == 0:
        returns = None
    else:
        returns = annotations.returns[0].type
        
    # These are the annotations
    name2type = dict([ (name, v.type) for (name, v) in annotations.params.items()])
    
    # Let's look at the parameters:
    args, varargs, varkw, defaults = inspect.getargspec(function) #@UnusedVariable
    
    # Check we don't have extra:
    for name in name2type:
        if not name in args:
            msg = 'Specified contract for param %r not found in %r.' % (name, args)
            raise ContractException(msg)
        
    if len(name2type) != len(args):
        msg = 'Found %d contracts for %d variables.' % (len(name2type), len(args))
        raise ContractException(msg)
    
    accepts = []
    for a in args:
        accepts.append(name2type[a])
        
    return accepts, returns

# utilities/friendly
def check(contract, object, desc=None):
    if not isinstance(contract, str):
        raise ValueError('I expect a string (contract spec) as the first '
                         'argument, not a %s.' % type(contract))
    try:
        return check_contracts([contract], [object])
    except ContractNotRespected as e:
        if desc is not None:
            e.error = '%s\n\nDetails:\n%s' % (desc, e.error)
        raise

def check_multiple(couples, desc=None):
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
