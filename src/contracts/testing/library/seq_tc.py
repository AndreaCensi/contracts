from . import good, fail


# sequences
good('seq', [])
good('seq', ())
good('seq', 'ciao')
fail('seq', {})
good('seq[*]', [])
good('seq[*]', [1])
good('seq[*](*)', [1])
good('seq[*](float)', [1.0])
fail('seq[*](float)', [1])
good('seq[*]', ())
good('seq[*]', (1,))
good('seq[*](*)', (1,))
good('seq[*](float)', (1.0,))
fail('seq[*](float)', (1,))

good('seq[=1]', [0])
good('seq[=2]', [0, 1])
fail('seq[=2]', [0])
good('seq[1]', [0])  # shortcut
good('seq[2]', (0, 1))
fail('seq[2]', (0,))

good('seq[N]', [])
good('seq[N],N>0', [1])
good('seq[N],N=1', [1])
good('seq[N],N>0,N<2', [1])
fail('seq[N],N>0', [])

good('seq[N]', ())
good('seq[N],N>0', (1,))
good('seq[N],N=1', (1,))
good('seq[N],N>0,N<2', (1,))
fail('seq[N],N>0', ())


