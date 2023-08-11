from pycompiler.compiler import SymbolTable, Symbol, GLOBALSCOPE


def test_define():
    table = SymbolTable()
    x = table.define("x")
    assert x == Symbol("x", GLOBALSCOPE, 0)

    y = table.define("y")
    assert y == Symbol("y", GLOBALSCOPE, 1)

def test_resolve():
    table = SymbolTable()
    x = table.define("x")
    y = table.define("y")

    assert table.resolve("x") == (True, Symbol("x", GLOBALSCOPE, 0))
    assert table.resolve("y") == (True, Symbol("y", GLOBALSCOPE, 1))
