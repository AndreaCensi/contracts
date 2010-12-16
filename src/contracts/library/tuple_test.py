from contracts.test_registrar import syntax_fail, good, fail

   
#### Tuples
good('tuple', ())
# tuples and lists are different
fail('tuple', [])
fail('list', ())
# tuples do not have the length
syntax_fail('tuple[*]')
syntax_fail('tuple[1]')
# you specify every element
good('tuple(*,*)', (1, 2))
good('tuple(*)', (1,))
fail('tuple(*,*)', (1, 2, 3))
good('tuple(int,int)', (1, 2))
good('tuple(int,float)', (1, 2.0))
fail('tuple(float,float)', (1, 2.0))
good('tuple(type(x),type(x))', (1, 2))
# something complicated: nested tuples
good('tuple(x, tuple(*,*,x))', (1, (2, 3, 1)))
fail('tuple(x, tuple(*,*,x))', (1, (2, 3, 2)))
good('tuple(type(x), tuple(*,*,type(x)))', (1, (2.1, 3.0, 3)))
fail('tuple(type(x), tuple(*,*,type(x)))', (1, (2.1, 3.0, 3.1)))
 
