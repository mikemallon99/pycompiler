from typing import Dict, Tuple, Any, Optional

Scope = str
GLOBALSCOPE: Scope = Scope("GLOBAL")
LOCALSCOPE: Scope = Scope("LOCAL")
FREESCOPE: Scope = Scope("FREE")
BUILTINSCOPE: Scope = Scope("BUILTIN")
FUNCTIONSCOPE: Scope = Scope("FUNCTION")


class Symbol:
    def __init__(self, name: str, scope: Scope, index: int):
        self.name: str = name
        self.scope: Scope = scope
        self.index: int = index

    def __eq__(self, other: Any):
        if not isinstance(other, Symbol):
            return NotImplemented
        return (
            self.name == other.name
            and self.scope == other.scope
            and self.index == other.index
        )

    def __repr__(self):
        return f"<Symbol: name={self.name}, scope={self.scope}, index={self.index}>"


class SymbolTable:
    def __init__(self, outer=None):
        self.store: Dict[str, Symbol] = {}
        self.outer = outer
        self.num_defs: int = 0
        self.free_symbols: List[Symbol] = []

    def define(self, name) -> Symbol:
        if self.outer:
            symbol = Symbol(name, LOCALSCOPE, self.num_defs)
        else:
            symbol = Symbol(name, GLOBALSCOPE, self.num_defs)
        self.store[name] = symbol
        self.num_defs += 1
        return symbol

    def define_builtin(self, index: int, name: str) -> Symbol:
        symbol = Symbol(name, BUILTINSCOPE, index)
        self.store[name] = symbol
        return symbol

    def define_free(self, original: Symbol) -> Symbol:
        self.free_symbols.append(original)
        symbol = Symbol(original.name, FREESCOPE, len(self.free_symbols) - 1)
        self.store[original.name] = symbol
        return symbol

    def define_function_name(self, name: str) -> Symbol:
        symbol = Symbol(name, FUNCTIONSCOPE, 0)
        self.store[name] = symbol
        return symbol

    def resolve(self, name) -> Tuple[bool, Symbol | None]:
        symbol = self.store.get(name)
        if not symbol and self.outer:
            _, symbol = self.outer.resolve(name)
            if not symbol:
                return bool(symbol), symbol

            if symbol.scope == GLOBALSCOPE or symbol.scope == BUILTINSCOPE:
                return bool(symbol), symbol

            free = self.define_free(symbol)
            return True, free
        return bool(symbol), symbol

