
def indent(s, prefix):
    lines = s.split('\n')
    lines = ['%s%s' % (prefix, line.rstrip()) for line in lines]
    return '\n'.join(lines)
