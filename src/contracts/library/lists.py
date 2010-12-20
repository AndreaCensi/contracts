from ..interface import Contract, ContractNotRespected
from ..syntax import add_contract, W, contract, O, S

class List(Contract):
    
    def __init__(self, length_contract=None, elements_contract=None, where=None):
        Contract.__init__(self, where)
        self.length_contract = length_contract
        self.elements_contract = elements_contract
    
    def check_contract(self, context, value): 
        if not isinstance(value, list):
            error = 'Expected a list, got %r.' % value.__class__.__name__
            raise ContractNotRespected(contract=self, error=error,
                                       value=value, context=context)
       
        if self.length_contract is not None:
            self.length_contract._check_contract(context, len(value))
        
        if self.elements_contract is not None:
            for i, element in enumerate(value): #@UnusedVariable
                # context2 = context.copy()
                # We should use the same context; perhaps we are breaking sthg?
                context2 = context
                self.elements_contract._check_contract(context2, element)
    
    def __str__(self):
        s = 'list'
        if self.length_contract is not None:
            s += '[%s]' % self.length_contract
        if self.elements_contract is not None:
            s += '(%s)' % self.elements_contract
        return s
    
    def __repr__(self):
        s = 'List(%r,%r)' % (self.length_contract, self.elements_contract)
        return s
            
    @staticmethod
    def parse_action(s, loc, tokens):
        where = W(s, loc)
        length_contract = tokens.get('length_contract', None)
        elements_contract = tokens.get('elements_contract', None)
        return List(length_contract, elements_contract, where=where)
 

list_contract = (S('list') + 
                 # allow shortcut: list[1] instead of list[=1]
                 O(S('[') + contract('length_contract') + S(']')) + 
                 O(S('(') + contract('elements_contract') + S(')')))
list_contract.setParseAction(List.parse_action)


add_contract(list_contract)
