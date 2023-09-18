from typing import List
from pycompiler.objects import (
    Object,
    IntObject,
    BooleanObject,
    NullObject,
    StringObject,
    ArrayObject,
    MapObject,
)


class Builtin(Object):
    def __init__(self, func, name):
        self.func = func
        self.name = name


def builtin_puts(args: List[Object]) -> Object | str:
    for arg in args:
        print(arg.value)
    return NullObject()


def builtin_first(args: List[Object]) -> Object | str:
    if len(args) != 1:
        return "wrong number of args: need 1"
    if not isinstance(args[0], ArrayObject):
        return "arg is wrong type, must be array"

    arr: List[Object] = args[0].value
    if len(arr) > 1:
        return args[0].value[0]
    return NullObject()


def builtin_last(args: List[Object]) -> Object | str:
    if len(args) != 1:
        return "wrong number of args: need 1"
    if not isinstance(args[0], ArrayObject):
        return "arg is wrong type, must be array"

    arr: List[Object] = args[0].value
    if len(arr) > 1:
        return args[0].value[-1]
    return NullObject()


def builtin_rest(args: List[Object]) -> Object | str:
    if len(args) != 1:
        return "wrong number of args: need 1"
    if not isinstance(args[0], ArrayObject):
        return "arg is wrong type, must be array"

    arr: List[Object] = args[0].value
    if len(arr) > 1:
        new_arr = []
        for obj in arr[1:]:
            new_arr.append(copy(obj))
        return ArrayObject(new_arr)
    return NullObject()


def builtin_push(args: List[Object]) -> Object | str:
    if len(args) != 2:
        return "wrong number of args: need 2"
    if not isinstance(args[0], ArrayObject):
        return "arg is wrong type, must be array"

    arr: List[Object] = args[0].value
    new_arr = []
    for obj in arr[1:]:
        new_arr.append(copy(obj))
    new_arr.append(args[1])
    return ArrayObject(new_arr)


def builtin_len(args: List[Object]) -> Object | str:
    if len(args) != 1:
        return "wrong number of args: need 1"
    if not isinstance(args[0], ArrayObject):
        return "arg is wrong type, must be array"
    return IntObject(len(args[0].value))


BUILTINS: List[Builtin] = [
    Builtin(builtin_len, "len"),
    Builtin(builtin_puts, "puts"),
    Builtin(builtin_first, "first"),
    Builtin(builtin_last, "last"),
    Builtin(builtin_push, "push"),
    Builtin(builtin_rest, "rest"),
]

