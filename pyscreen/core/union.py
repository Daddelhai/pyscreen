from typing import TypeVar, Generic

T1 = TypeVar('T1')
T2 = TypeVar('T2')
R = TypeVar('R')

class Union2(Generic[T1, T2]):
    def __init__(self, obj1: T1, obj2: T2):
        self.obj1 = obj1
        self.obj2 = obj2

    def get(self, cls: type[R])->R:
        if isinstance(self.obj1, cls):
            return self.obj1
        elif isinstance(self.obj2, cls):
            return self.obj2
        else:
            raise TypeError("Invalid type")
