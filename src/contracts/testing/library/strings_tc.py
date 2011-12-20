from . import syntax_fail, good, fail


### Strings
good('str', 'ciao')
good('string', 'ciao', exact=False)
fail('str', list('ciao'))  # sequences of chars are not str
# Can specify the length
good('str[N]', '')
good('str[1]', 'a')
good('str[2]', 'ab')
good('str[>0]', 'ab')
fail('str[>0]', '')
good('str[N],N>3', 'ciao')
fail('str[N],N>3', 'cia')
# Cannot specify anything on the content
syntax_fail('str(*)')
