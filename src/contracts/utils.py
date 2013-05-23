
def indent(s, prefix):
    lines = s.split('\n')
    lines = ['%s%s' % (prefix, line) for line in lines]
    return '\n'.join(lines)
