from ..interface import Contract, ContractNotRespected
from ..syntax import  W, contract, O, S, add_contract


class Dict(Contract):
    
    def __init__(self, length=None, key_c=None, value_c=None, where=None):
        Contract.__init__(self, where)
        self.length = length
        self.key_c = key_c
        self.value_c = value_c
        
    def check_contract(self, context, value):         
        if not isinstance(value, dict):
            error = 'Expected a dict, got %r.' % value.__class__.__name__
            raise ContractNotRespected(contract=self, error=error,
                                       value=value, context=context)
        
        if self.length is not None:
            self.length.check_contract(context, len(value))
        
        for k, v in value.items():
            if self.key_c is not None:
                self.key_c.check_contract(context, k)
            if self.value_c is not None:
                self.value_c.check_contract(context, v)
    
    def __str__(self):
        s = 'dict'
        if self.length is not None:
            s += '[%s]' % self.length
        if self.key_c is not None:
            k = str(self.key_c)
        else:
            k = ''
        if self.value_c is not None:
            v = str(self.value_c)
        else:
            v = ''
        if k or v:
            s += '(%s:%s)' % (k, v)
        return s
    
    def __repr__(self):
        return 'Dict(%r,%r,%r)' % (self.length, self.key_c, self.value_c)
        
            
    @staticmethod
    def parse_action(s, loc, tokens):
        where = W(s, loc)
        if 'length' in tokens:
            length = tokens['length']
        else:
            length = None
            
        if 'key' in tokens:
            key = tokens['key']
        else: 
            key = None
        
        if 'value' in tokens:
            value = tokens['value']
        else: 
            value = None

        return Dict(length, key, value, where=where)
 

length_spec = S('[') + contract('length') + S(']')
kv_spec = '(' + O(contract('key')) + ':' + O(contract('value')) + ')'
dict_contract = 'dict' + O(length_spec) + O(kv_spec)

dict_contract.setParseAction(Dict.parse_action)

add_contract(dict_contract)

