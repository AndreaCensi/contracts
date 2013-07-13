from contracts.interface import Contract, ContractNotRespected
from contracts.syntax import W, S, Keyword, add_contract, add_keyword
from pyparsing import alphanums, Word


class IsInstance(Contract):
    
    """ Checks that one of the superclasses have the specified name. """
     
    def __init__(self, name, where=None):
        Contract.__init__(self, where)
        self.name = name

    def check_contract(self, context, value):
        #  self.type_constraint._check_contract(context, type(value))

        if hasattr(value, '__class__'):
            # old style class
            class_name = value.__class__.__name__
            bases_names = [x.__name__ for x in value.__class__.__bases__]
        else:
            # new style
            t = type(value)
            class_name = t.__name__
            bases = t.__bases__
            bases_names = [b.__name__ for b in bases]

        if not self.name in bases_names + [class_name]:
            msg = ('Failed check isinstance(%s) for type %r and superclasses %r.' 
                   % (self.name, class_name, bases_names))
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


Identifier = Word(alphanums + '_')

isinstance_contract = (Keyword('isinstance') - S('(')
                 - Identifier('name') - S(')'))

add_contract(isinstance_contract.setParseAction(IsInstance.parse_action))
add_keyword('isinstance')
