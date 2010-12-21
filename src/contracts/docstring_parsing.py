from collections import namedtuple
import re

Arg = namedtuple('Arg', 'name type')

class Arg:
    def __init__(self, desc=None, type=None):
        if desc is not None:
            desc = desc.strip()
        self.desc = desc
        if type is not None:
            type = type.strip()
        self.type = type
    def __eq__(self, other):
        return (self.type == other.type and 
                self.desc == other.desc)
               
    def __repr__(self):
        return "Arg(%r,%r)" % (self.desc, self.type)

class DocStringInfo:
    def __init__(self, docstring=None, params={}, returns=[]):
        self.docstring = docstring
        self.params = params
        self.returns = returns
        # self.vars
        # self.raises
    
    def __eq__(self, other):
        return (self.docstring == other.docstring and
                self.params == other.params and
                self.returns == other.returns)
    
     
    def __str__(self):
        s = "DocString:\n"
        s += ' params: %s\n' % self.params
        s += ' returns: %s' % self.returns
        return s
        
def parse_annotations(docstring, keys, empty=False):
    ''' Returns docstring_without, dictionary.
        If empty specified, will look for empty statements, and give integers
        for names. 
    '''
    assert docstring is not None
        
    found = {}
    
    for key in keys:
        if empty:
            regexp = '^\s*:\s*%s\s*:\s*(?P<desc>.*?)\s*$' % key
        else:
            regexp = '^\s*:\s*%s\s+(?P<name>\w*?)\s*:\s*(?P<desc>.*?)\s*$' % key
        regexp = re.compile(regexp, re.MULTILINE)
        
        def replace(match):
            d = match.groupdict()
                            
            if empty:
                name = len(found)
            else:
                name = d['name']
                
            found[name] = d['desc']
                
            return ""
         
        docstring = regexp.sub(repl=replace, string=docstring)
        
    return docstring, found
    
def parse_docstring_annotations(docstring):
    assert docstring is not None
        
    param_keys = ['param', 'parameter', 'arg', 'argument', 'key', 'keyword']
    type_keys = ['type']
    return_keys = ['returns', 'return']
    rtype_keys = ['rtype']
    # TODO: document state?
    # var_keys = ['var', 'ivar', 'cvar']
    # raises, raise, except, exception
    
    docstring, params_ann = parse_annotations(docstring, param_keys, False) 
    docstring, types_ann = parse_annotations(docstring, type_keys, False)
    docstring, returns_ann = parse_annotations(docstring, return_keys, True)
    docstring, rtype_ann = parse_annotations(docstring, rtype_keys, True)
    
    params = {}
    names = set(list(params_ann.keys()) + list(types_ann.keys()))
    for name in names:
        params[name] = Arg(params_ann.get(name, None),
                            types_ann.get(name, None))

    returns = []
    for i in range(max(len(returns_ann), len(rtype_ann))):
        returns.append(Arg(returns_ann.get(i, None),
                            rtype_ann.get(i, None)))

    return DocStringInfo(docstring, params=params, returns=returns)

 
