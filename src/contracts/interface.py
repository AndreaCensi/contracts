from procgraph.core.exceptions import add_prefix
from copy import deepcopy

class ContractException(Exception):
    pass

class ContractSyntaxError(ContractException):
    ''' A syntactic error by who wrote the model spec.'''
    def __init__(self, error, where=None):
        self.error = error
        self.where = where
        
    def __str__(self):
        s = self.error
        s += "\n\n" + add_prefix(self.where.__str__(), ' ')
        return s 

    
class ContractNotRespected(ContractException):
    
    def __init__(self, contract, error, value, context):
        self.contract = contract
        self.error = error
        self.value = value
        self.context = context
        
    def __str__(self):
        msg = 'Contract breach: ' + str(self.error) + '\n'
        msg += '- context: %r\n' % self.context
        msg += '- contract: %r\n' % self.contract
        return msg
    
class ContractSemanticError(ContractException):
    
    def __init__(self, contract, error, context):
        self.contract = contract
        self.error = error
        self.context = context
        
    def __str__(self):
        msg = 'Contract semantic error: ' + str(self.error) + '\n'
        msg += '- context: %r\n' % self.context
        msg += '- contract: %r\n' % self.contract
        return msg
        
class BoundVariable:
    def __init__(self, value, description, origin):
        self.value = value
        self.description = description
        self.origin = origin
        
    def __repr__(self):
        return "%r" % self.value

class RValue:
    def eval(self, context):
        pass
    
class VariableRef(RValue):
    def __init__(self, where, variable):
        self.variable = variable
        self.where = where
        
    def eval(self, context):
        var = self.variable
        if not context.has_variable(var):
            msg = 'Unknown variable %r.' % var
            raise ContractSemanticError(None, msg, context)
        return context.get_variable(var)

    def __repr__(self):
        return self.variable

class Context:
    ''' Class that represents the context for checking an expression. '''
        
    def __init__(self):
        self._variables = {}
        
    def has_variable(self, name):
        return name in self._variables
    
    def get_variable(self, name):
        assert self.has_variable(name)
        return self._variables[name].value
    
    def set_variable(self, name, value, description=None, origin=None):
        assert not self.has_variable(name)
        # print 'Set %s = %r' % (name, value)
        self._variables[name] = BoundVariable(value, description, origin)
    
    def eval(self, value, contract_ref=None): # XXX:
        if isinstance(value, RValue):
            return value.eval(self)
        else:
            return value

    def copy(self):
        ''' Returns a copy of this context. '''
        return deepcopy(self)
    
    def __repr__(self):
        return 'Context(%r)' % self._variables
        
class Contract:
    
    def __init__(self, where):
        from procgraph.core.parsing_elements import Where
        assert isinstance(where, Where)
        self.where = where
    
    def check_contract(self, context, value):
        ''' 
            Checks that value is ok with this contract in the specific 
            context. 
        '''
        raise ValueError('You did not implement check_contract() for %s.' % 
                         self.__class__.__name__)
    
    
    
    
    
    
