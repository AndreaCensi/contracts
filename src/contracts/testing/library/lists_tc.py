from . import good, fail


# lists
good('list', [])
fail('list', 'ciao')
good('list[*]', [])
good('list[*]', [1])
good('list[*](*)', [1])
good('list[*](float)', [1.0])
fail('list[*](float)', [1])
good('list[=1]', [0])
good('list[=2]', [0, 1])
fail('list[=2]', [0])
good('list[1]', [0])  # shortcut
good('list[2]', [0, 1])
fail('list[2]', [0])
good('list(int)', [])
good('list(int)', [0, 1])
fail('list(int)', [0, 'a'])
fail('list(int)', [0, 'a'])
good('list(int,>0)', [2, 1])
fail('list(int,>0)', [0, 1])
good('list(int,=0)', [0, 0])
# with parametric lengths 
good('list[N]', [])
good('list[N],N>0', [1])
good('list[N],N=1', [1])
good('list[N],N>0,N<2', [1])
fail('list[N],N>0', [])

