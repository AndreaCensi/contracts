from .  import good, fail

# dictionary of string -> tuple, with tuple of two elements with different type
# In this case, each value should have the same two types
good('dict(str:tuple(type(x),type(y))),x!=y', {'a': (2, 1.1)})
fail('dict(str:tuple(type(x),type(y))),x!=y', {'a': (2, 1)})

# This fails because we have x=int,y=float followed by float,int
fail('dict(str:tuple(type(x),type(y))),x!=y', {'a': (2, 1.1), 'b': (1.1, 2)})

# Here we force the context to not match using $(...) 
good('dict(str:$(tuple(type(x),type(y)),x!=y))', {'a': (2, 1.1),
                                                  'b': (1.1, 2)})
fail('dict(str:$(tuple(type(x),type(y)),x!=y))', {'a': (2, 1)})
