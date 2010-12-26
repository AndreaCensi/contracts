import operator

from ..syntax import (Combine, Word, alphas, alphanums, oneOf,
                      ParseSyntaxException, ParseException)

def find_longest_match(s, options):
    matches = [(x, longest_match(s, x)) for x in options]
    best = max(matches, key=operator.itemgetter(1))
    return best

def longest_match(a, b):
    lengths = range(min(len(a), len(b)) + 1)
    lengths.reverse()
    for i in lengths:
        if a[:i] == b[:i]:
            return i
    assert False

assert ('float64', 6) == find_longest_match('float6', ['float32', 'float64'])
                                            
def default_message(identifier):
    return 'Unknown identifier %r. ' % identifier

def create_suggester(get_options, get_message=default_message):

    patterns = Combine(oneOf(list(alphas)) + Word('_' + alphanums))

    def parse_action(s, loc, tokens):
        identifier = tokens[0]
        options = get_options()
        assert not (identifier in options), 'I was not supposed to match %r.' % identifier
        
        msg = get_message(identifier)

        if options:
            match, length = find_longest_match(identifier, options)
            if length > 1:
                msg += 'Did you mean %r?' % match
                loc += length
            else:
                msg += '\nI know: %r.\n' % (options)
        pe = ParseException(s, loc, msg, patterns) 
        raise ParseSyntaxException(pe) 
    
    patterns.setParseAction(parse_action)
    
    return patterns
