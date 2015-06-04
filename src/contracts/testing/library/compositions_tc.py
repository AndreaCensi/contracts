from . import good, fail

# AND
fail('=0,=1', 0)
good('=0,>=0', 0)

# OR
good('=0|=1', 0)
good('=0|=1', 1)
fail('=0|=1', 2)

# NOT
fail('!1', 1)
good('!None', 1)
fail('!(1|2)', 1)
good('!(0|None)', 3)


good('0|1|2', 2)
good('0|1|2', 1)

good('0|2', 2)
good('0|1|2', 2)
good('0|1|2|3', 2)
good('0|1|2|3|4', 2)
good('0|1|2|3|4|5', 2)

good('list(0|1)', [0, 1, 0])
fail('list(0|1)', [0, 1, 2])


# Check logic and precedence
# & has more precedence than |

good('*|#', None)
good('*|(#,*)', None, exact=False)
good('*|(*,#)', None, exact=False)
good('*|*,#', None)
fail('(*|*),#', None)
good('*,*|#', None)
good('*,#|*', None)
good('*|#|*', None)
fail('*,#,*', None)
fail('*,#|#', None)
good('#|*,(#|*)', None)


# ! has lower precedence than | or &
good('!#|*', None)
fail('!(#|*)', None)
fail('!*,#', None)
good('!(*,#)', None)
