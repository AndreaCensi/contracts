from ..interface import Contract, ContractNotRespected
from ..syntax import add_contract, W, contract, O, S, ZeroOrMore, simple_contract

class Tuple(Contract):
    
    def __init__(self, length=None, elements=None, where=None):
        Contract.__init__(self, where)
        self.length = length
        self.elements = elements
        assert elements is None or isinstance(elements, list)
        if elements:
            for e in elements:
                assert isinstance(e, Contract)
        
    def check_contract(self, context, value): 
        if not isinstance(value, tuple):
            error = 'Expected a tuple, got %r.' % value.__class__.__name__
            raise ContractNotRespected(contract=self, error=error,
                                       value=value, context=context)
       
        if self.length is not None:
            self.length.check_contract(context, len(value))
        
        if self.elements is not None:
            if len(value) != len(self.elements):
                error = ('Expected a tuple of length %s, got %r of length %s.' % 
                         (len(self.elements), value, len(value)))
                raise ContractNotRespected(contract=self, error=error,
                                           value=value, context=context)
       
            for i in range(len(value)):
                self.elements[i].check_contract(context, value[i])
    
    def __repr__(self):
        return 'Tuple(%r,%r)' % (self.length, self.elements)
    
    def __str__(self):
        s = 'tuple'
        if self.length is not None:
            s += '[%s]' % self.length
        if self.elements is not None:
            s += '(%s)' % ",".join("%s" % x for x in self.elements)
        return s
            
    @staticmethod
    def parse_action(s, loc, tokens): 
        where = W(s, loc)
        length = tokens.get('length', None)
        if 'elements' in tokens:
            elements = list(tokens['elements'])
        else: 
            elements = None
        assert elements is None or length is None
        return Tuple(length, elements, where=where)
 

# if you use contract instead of simple_contract, it will be matched as And
elements = (S('(') + 
             simple_contract + ZeroOrMore(S(',') + simple_contract)
              + S(')'))('elements')
length = S('[') + contract('length') + S(']')

tuple_contract = S('tuple') + O(length | elements) 

add_contract(tuple_contract.setParseAction(Tuple.parse_action))
