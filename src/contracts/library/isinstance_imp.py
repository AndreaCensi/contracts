#cython: language_level=3, annotation_typing=True, c_string_encoding=utf-8, boundscheck=False, wraparound=False, initializedcheck=False
from ..interface import Contract, ContractNotRespected
from Aspidites._vendor.contracts.syntax import W, S, Keyword, add_contract, add_keyword
from Aspidites._vendor.pyparsing import alphanums, Word

__all__ = ['IsInstance', 'isinstance_contract']

class IsInstance(Contract):
    
    """ Checks that one of the superclasses have the specified name. """
     
    def __init__(self, name, where=None):
        Contract.__init__(self, where)
        self.name = name

    def check_contract(self, context, value, silent):
        class_name, bases_names = get_all_super_names(value) 
        
        options = bases_names + [class_name]
        if not self.name in options:
            
            msg = ('Failed check isinstance(%s) for type %r and superclasses %r.' 
                   % (self.name, class_name, bases_names))
            
            # Check it is just a case problem
            lc_name = self.name.lower()
            lc_options = [x.lower() for x in options]
            if lc_name in lc_options:
                msg += '\n***Note: this is just a lower/upper case error!***'

            raise ContractNotRespected(self, msg, value, context)

    def __str__(self):
        return 'isinstance(%s)' % self.name

    def __repr__(self):
        return 'IsInstance(%r)' % self.name

    @staticmethod
    def parse_action(s, loc, tokens):
        where = W(s, loc)
        name = tokens['name']
        return IsInstance(name, where)


def get_all_super_names(value):
    """ Returns name of class, list of names of supers """
    if hasattr(value, '__class__'):
        # old style class
        klass = value.__class__
        class_name = klass.__name__
        bases = get_oldstyle_bases(klass)
        bases_names = [x.__name__ for x in bases]
    else:
        # new style
        t = type(value)
        class_name = t.__name__
        bases_names = [b.__name__ for b in t.mro()]
    return class_name, bases_names

def get_oldstyle_bases(klass):
    todo = [klass]
    res = []
    while todo:
        x = todo.pop(0)
        res.append(x)
        for b in x.__bases__:
            if not b in res:
                todo.append(b)
    return res

Identifier = Word(alphanums + '_')

isinstance_contract = (Keyword('isinstance') - S('(') - Identifier('name') - S(')'))

add_contract(isinstance_contract.setParseAction(IsInstance.parse_action))
add_keyword('isinstance')
