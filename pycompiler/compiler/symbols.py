from typing import Dict, Tuple, Any

Scope = str
GLOBALSCOPE: Scope = Scope("GLOBAL")


class Symbol:
    def __init__(self, name: str, scope: Scope, index: int):
        self.name: str = name
        self.scope: Scope = scope
        self.index: int = index

    def __eq__(self, other: Any):
        if not isinstance(other, Symbol):
            return NotImplemented
        return self.name == other.name and self.scope == other.scope and self.index == other.index

    def __repr__(self):
        return f"<Symbol: name={self.name}, scope={self.scope}, index={self.index}>"


class SymbolTable:
    def __init__(self):
        self.store: Dict[str, Symbol] = {}
        self.num_defs: int = 0

    def define(self, name) -> Symbol:
        symbol = Symbol(name, GLOBALSCOPE, self.num_defs)
        self.store[name] = symbol
        self.num_defs += 1
        return symbol

    def resolve(self, name) -> Tuple[bool, Symbol]:
        symbol = self.store.get(name)
        return bool(symbol), symbol
