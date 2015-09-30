import operator


def find_longest_match(s, options):
    matches = [(x, longest_match(s, x)) for x in options]
    best = max(matches, key=operator.itemgetter(1))
    return best


def longest_match(a, b):
    lengths = range(min(len(a), len(b)) + 1)
    lengths = list(reversed(lengths))
    for i in lengths:
        if a[:i] == b[:i]:
            return i
    assert False  # pragma: no cover

assert ('float64', 6) == find_longest_match('float6', ['float32', 'float64'])
assert 2 == find_longest_match('fl6', ['float32', 'float64'])[1]


# http://hetland.org/coding/python/levenshtein.py
def levenshtein(a, b):
    """Calculates the Levenshtein distance between a and b."""
    n, m = len(a), len(b)
    if n > m:  # pragma: no cover
        # Make sure n <= m, to use O(min(n,m)) space
        a, b = b, a
        n, m = m, n

    current = range(n + 1)
    for i in range(1, m + 1):
        previous, current = current, [i] + [0] * n
        for j in range(1, n + 1):
            add, delete = previous[j] + 1, current[j - 1] + 1
            change = previous[j - 1]
            if a[j - 1] != b[i - 1]:
                change = change + 1
            current[j] = min(add, delete, change)

    return current[n]


def find_best_match(s, options):
    matches = [(x, levenshtein(s[:len(x)], x) - len(x)) for x in options]
    best = min(matches, key=operator.itemgetter(1))
    return best


def default_message(identifier):
    return 'Unknown identifier %r. ' % identifier


def create_suggester(get_options, get_message=default_message,
            pattern=None):

    from ..syntax import (Combine, Word, alphas, alphanums, oneOf,
                      ParseSyntaxException, ParseException)
    if pattern is None:
        pattern = Combine(oneOf(list(alphas)) + Word('_' + alphanums))


    pattern = pattern.copy()

    def find_match(identifier, options, local_string):
        match, length = find_longest_match(identifier, options)
        if length >= 2:
            return True, match, length

        match, distance = find_best_match(local_string, options)

        if distance < len(match) - 1:
            length = longest_match(local_string, match)
            return True, match, length

        return False, "No matches found", 0

    def parse_action(s, loc, tokens):
        identifier = tokens[0]
        options = get_options()
        
        msg = 'Bug in syntax: I was not supposed to match %r.' % identifier
        msg += '(options: %s)' % options
        
        msg += ''' Suggestions on the cause:
            1) Use add_keyword(), always.
            
            2) Use:
                Keyword('attr') - attrs_spec
               instead of 
                Keyword('attr') + attrs_spec
        '''
        assert not (identifier in options), msg

        
        msg = get_message(identifier)

        if options:
            local_string = s[loc:]
            confident, match, length = find_match(identifier, options,
                                                  local_string)
            if confident:
                msg += 'Did you mean %r?' % match
                loc += length
            else:
                msg += '\nI know: %r.\n' % (options)
        pe = ParseException(s, loc, msg, pattern)
        raise ParseSyntaxException(pe)

    pattern.setParseAction(parse_action)

    return pattern
