import operator

from ..interface import Contract, ContractNotRespected, describe_value
from ..syntax import (Combine, Word, W, alphas, alphanums, oneOf,
                      ParseSyntaxException, ParseException)

def find_longest_match(s, options):
    matches = [(x, longest_match(s, x)) for x in options]
    return max(matches, key=operator.itemgetter(1))

def longest_match(a, b):
    lengths = range(min(len(a), len(b)))
    for i in lengths[::-1]:
        if a[:i] == b[:i]:
            return i
    assert False

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
                loc += length + 1
            else:
                msg += '\nI know: %r.\n' % (options)
        pe = ParseException(s, loc, msg, patterns) 
        raise ParseSyntaxException(pe) 
    
    patterns.setParseAction(parse_action)
    
    return patterns
