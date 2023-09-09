from typing import Dict, List, Tuple
from pycompiler.parser import FunctionLiteral
from pycompiler.code import Instructions, instructions_to_str



class Object:
    pass


class NullObject(Object):
    def __eq__(self, other: object):
        if not isinstance(other, NullObject):
            return NotImplemented
        return True

    def __repr__(self):
        return f"<NullObject>"


class IntObject(Object):
    def __init__(self, value: int):
        self.value: int = value

    def __eq__(self, other: object):
        if not isinstance(other, IntObject):
            return NotImplemented
        return self.value == other.value

    def __repr__(self):
        return f"<IntObject: value={self.value}>"

    def __hash__(self):
        return hash(self.value)


class StringObject(Object):
    def __init__(self, value: str):
        self.value: str = value

    def __eq__(self, other: object):
        if not isinstance(other, StringObject):
            return NotImplemented
        return self.value == other.value

    def __repr__(self):
        return f"<StringObject: value={self.value}>"

    def __hash__(self):
        return hash(self.value)


class ArrayObject(Object):
    def __init__(self, value: List[Object]):
        self.value: List[Object] = value

    def get(self, index: IntObject) -> Object:
        if index.value < 0 or index.value > (len(self.value) - 1):
            return NullObject()
        return self.value[index.value]

    def __eq__(self, other: object):
        if not isinstance(other, ArrayObject):
            return NotImplemented
        return self.value == other.value

    def __repr__(self):
        return f"<ArrayObject: value={self.value}>"

    def __hash__(self):
        return hash(self.value)


class MapObject(Object):
    def __init__(self, value: Dict[Object, Object]):
        self.value: Dict[Object, Object] = value

    def get(self, key: Object) -> Object:
        value = self.value.get(key)
        if not value:
            return NullObject()
        return self.value[key]

    def __eq__(self, other: object):
        if not isinstance(other, MapObject):
            return NotImplemented
        return self.value == other.value

    def __repr__(self):
        return f"<MapObject: value={self.value}>"


class FunctionObject(Object):
    def __init__(self, value: FunctionLiteral):
        self.value: FunctionLiteral = value
        self.environment = None

    def __eq__(self, other: object):
        if not isinstance(other, FunctionObject):
            return NotImplemented
        return self.value == other.value

    def __repr__(self):
        return f"<FunctionObject: value={self.value}>"


class CompiledFunctionObject(Object):
    def __init__(self, value: Instructions, num_locals: int, num_args: int):
        self.value: Instructions = value
        self.num_locals: int = num_locals
        self.num_args: int = num_args

    def __eq__(self, other: object):
        if not isinstance(other, CompiledFunctionObject):
            return NotImplemented
        return (
            self.value == other.value 
            and self.num_locals == other.num_locals 
            and self.num_args == other.num_args
        )

    def __repr__(self):
        return f"<CompiledFunctionObject: value={instructions_to_str(self.value)}>"


class BooleanObject(Object):
    def __init__(self, value: bool):
        self.value: bool = value

    def __eq__(self, other: object):
        if not isinstance(other, BooleanObject):
            return NotImplemented
        return self.value == other.value

    def __repr__(self):
        return f"<BooleanObject: value={self.value}>"


class ReturnObject(Object):
    def __init__(self, value: Object):
        self.value = value

    def __eq__(self, other: object):
        if not isinstance(other, ReturnObject):
            return NotImplemented
        return self.value == other.value

    def __repr__(self):
        return f"<ReturnObject: value={self.value}>"
