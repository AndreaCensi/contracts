from . import syntax_fail, good, fail

   
#### Tuples
good('tuple', ())
good('tuple', (1,))
# tuples and lists are different
fail('tuple', [])
fail('list', ())
# tuples can have the length
good('tuple[*]', (2, 2))
good('tuple[1]', (1,))
# you cannot specify every element
good('tuple(*,*)', (1, 2))
good('tuple(*)', (1,))
fail('tuple(*,*)', (1, 2, 3))
good('tuple(int,int)', (1, 2))
good('tuple(int,float)', (1, 2.0))
fail('tuple(float,float)', (1, 2.0))
good('tuple(type(x),type(x))', (1, 2))
# something complicated: nested tuples
good('tuple(x,tuple(*,*,x))', (1, (2, 3, 1)))
fail('tuple(x,tuple(*,*,x))', (1, (2, 3, 2)))
good('tuple(type(x),tuple(*,*,type(x)))', (1, (2.1, 3.0, 3)))
fail('tuple(type(x),tuple(*,*,type(x)))', (1, (2.1, 3.0, 3.1)))
# cannot specify both, even if coherent
syntax_fail('tuple[*](*,*)')

good('tuple(0,1|2)', (0, 2))
good('tuple(0,1|2)', (0, 2))
good('tuple(0,1|2|3)', (0, 3))
good('tuple(0,1|2|3,4)', (0, 3, 4))
fail('tuple(0,1|2)', (0, 3))
good('tuple(0,1,2)', (0, 1, 2))
good('tuple(1|2,3)', (1, 3))
good('tuple(1,(>2,int))', (1, 3))
fail('tuple(1,(>2,int))', (1, 3.0))
good('tuple(1,(*,*),2)', (1, 3, 2))
good('tuple(str,(str[1],str))', ('a', 'b'))
