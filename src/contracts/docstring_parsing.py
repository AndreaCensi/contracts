#cython: language_level=3, annotation_typing=True, c_string_encoding=utf-8, boundscheck=False, wraparound=False, initializedcheck=False
import re

import cython


class Arg(object):
    def __init__(self, desc=None, type=None):  # @ReservedAssignment
        if desc is not None:
            desc = desc.strip()
        self.desc = desc
        if type is not None:
            type = type.strip()  # @ReservedAssignment
        self.type = type

    def __eq__(self, other):
        return (self.type == other.type and
                self.desc == other.desc)

    def __repr__(self):
        return "Arg(%r,%r)" % (self.desc, self.type)


class DocStringInfo(object):
    def __init__(self, docstring=None, params=None, returns=None):
        if params is None:
            params = {}
        if returns is None:
            returns = []
        self.docstring = docstring
        self.params = params
        self.returns = returns

    def __eq__(self, other):
        return (self.docstring == other.docstring and
                self.params == other.params and
                self.returns == other.returns)

    def __repr__(self):
        return ("DocString(\n\t%r,\n\t%r,\n\t%r)" %
                (self.docstring, self.params, self.returns))

    def __str__(self):
        s = self.docstring
        valid_lines = [x for x in self.docstring.split('\n') if x]
        if valid_lines:
            last_line = [-1]
            indentation = number_of_spaces(last_line)
        else:
            indentation = 0
        # ORDER?
        s += '\n\n'
        prefix = '\n' + (' ' * indentation)
        for param in self.params:
            if self.params[param].desc is not None:
                s += (prefix + ':param %s: %s'
                      % (param, self.params[param].desc))
            if self.params[param].type is not None:
                s += (prefix + ':type %s:  %s'
                      % (param, self.params[param].type))
            s += prefix

        if self.returns:
            for r in self.returns:
                if r.desc is not None:
                    s += prefix + ':returns: %s' % (r.desc)
                if r.type is not None:
                    s += prefix + ':rtype:  %s' % (r.type)
                s += prefix

        return s

    @staticmethod
    def parse(docstring):
        assert docstring is not None

        param_keys = ['param', 'parameter', 'arg',
                      'argument', 'key', 'keyword']
        type_keys = ['type']
        return_keys = ['returns', 'return']
        rtype_keys = ['rtype']
        # var_keys = ['var', 'ivar', 'cvar']
        # raises, raise, except, exception

        docstring, params_ann = parse_annotations(docstring, param_keys, False,
                                                  True)
        docstring, types_ann = parse_annotations(docstring, type_keys, False,
                                                 False)
        docstring, returns_ann = parse_annotations(docstring, return_keys,
                                                   True, True)
        docstring, rtype_ann = parse_annotations(docstring, rtype_keys, True,
                                                 False)

        params = {}
        names = set(list(params_ann.keys()) + list(types_ann.keys()))
        for name in names:
            param_type, param_desc = params_ann.get(name, (None, None))
            params[name] = Arg(param_desc,
                               param_type or types_ann.get(name, None))

        returns = []
        for i in range(max(len(returns_ann), len(rtype_ann))):
            return_type, return_desc = returns_ann.get(i, (None, None))
            returns.append(Arg(return_desc,
                               return_type or rtype_ann.get(i, None)))

        return DocStringInfo(docstring, params=params, returns=returns)


def parse_annotations(docstring, keys, empty=False, inline_type=False):
    """
        Parses ":key name: description" lines into a dictionary mapping name to
        a description.

        If empty is specified, look statements without a name such as
        ":key: description".

        If inline_type is specified, allow an optional type to be specified
        parsing ":key type name: description" or ":key type: description".
    """
    assert docstring is not None

    found = {}

    def replace(match):
        d = match.groupdict()

        if empty:
            name = len(found)
        else:
            name = d['name'] or None

        if inline_type:
            found[name] = (d['type'] or None, d['desc'] or None)
        else:
            found[name] = d['desc'] or None
        return ""

    for key in keys:
        if empty:
            regexp = fr'^\s*:\s*{key}(?P<type>[^:]*?)\s*:\s*(?P<desc>.*?)\s*$'
        else:
            regexp = rf'^\s*:\s*{key}\s+(?P<type>[^:]*?)(?P<name>[^\s:]+)\s*:\s*(?P<desc>.*?)\s*$'
        regexp = re.compile(regexp, re.MULTILINE)

        docstring = regexp.sub(repl=replace, string=docstring)

    return docstring, found


def number_of_spaces(x):
    x: cython.int
    i: cython.int
    for i in range(1, len(x)):
        if x[:i] != ' ' * i:
            return i - 1
    return len(x)
