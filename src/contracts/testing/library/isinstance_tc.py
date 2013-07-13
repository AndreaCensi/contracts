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
