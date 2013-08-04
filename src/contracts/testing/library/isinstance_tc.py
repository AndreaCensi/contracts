from . import good, fail

class BaseClass():
    pass

class SubClass(BaseClass):
    pass

good('isinstance(BaseClass)', BaseClass())
good('isinstance(BaseClass)', SubClass())
good('isinstance(SubClass)', SubClass())
fail('isinstance(SubClass)', BaseClass())

class BaseClass2(object):
    pass

class SubClass2(BaseClass2):
    pass

good('isinstance(BaseClass2)', BaseClass2())
good('isinstance(BaseClass2)', SubClass2())
good('isinstance(SubClass2)', SubClass2())
fail('isinstance(SubClass2)', BaseClass2())

# Let's try with 3, old-style

class BaseClass3():
    pass

class MidClass3(BaseClass3):
    pass

class SubClass3(MidClass3):
    pass

good('isinstance(BaseClass3)', BaseClass3())
good('isinstance(BaseClass3)', SubClass3())
good('isinstance(SubClass3)', SubClass3())
fail('isinstance(SubClass3)', BaseClass3())

class BaseClass4(object):
    pass

class MidClass4(BaseClass4):
    pass

class SubClass4(MidClass4):
    pass

good('isinstance(BaseClass4)', BaseClass4())
good('isinstance(BaseClass4)', SubClass4())
good('isinstance(SubClass4)', SubClass4())
fail('isinstance(SubClass4)', BaseClass4())

