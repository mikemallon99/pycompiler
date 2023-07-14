from pycompiler.parser import FunctionLiteral

class Object:
    pass

class IntObject(Object):
    def __init__(self, value: int):
        self.value: int = value

    def __eq__(self, other: Object):
        if not isinstance(other, IntObject):
            return NotImplemented
        return self.value == other.value

    def __repr__(self):
        return f"<IntObject: value={self.value}>"

class StringObject(Object):
    def __init__(self, value: str):
        self.value: str = value

    def __eq__(self, other: Object):
        if not isinstance(other, StringObject):
            return NotImplemented
        return self.value == other.value

    def __repr__(self):
        return f"<StringObject: value={self.value}>"

class FunctionObject(Object):
    def __init__(self, value: bool):
        self.value: FunctionLiteral = value
        self.environment = None

    def __eq__(self, other: Object):
        if not isinstance(other, FunctionObject):
            return NotImplemented
        return self.value == other.value

    def __repr__(self):
        return f"<FunctionObject: value={self.value}>"

class BooleanObject(Object):
    def __init__(self, value: bool):
        self.value: bool = value

    def __eq__(self, other: Object):
        if not isinstance(other, BooleanObject):
            return NotImplemented
        return self.value == other.value

    def __repr__(self):
        return f"<BooleanObject: value={self.value}>"

class ReturnObject(Object):
    def __init__(self, value: Object):
        self.value = value

    def __eq__(self, other: Object):
        if not isinstance(other, ReturnObject):
            return NotImplemented
        return self.value == other.value

    def __repr__(self):
        return f"<ReturnObject: value={self.value}>"

