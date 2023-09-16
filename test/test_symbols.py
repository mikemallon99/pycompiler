from pycompiler.compiler import (
    SymbolTable, 
    Symbol, 
    GLOBALSCOPE,
    BUILTINSCOPE,
    LOCALSCOPE
)


def test_define():
    table = SymbolTable()
    x = table.define("x")
    assert x == Symbol("x", GLOBALSCOPE, 0)

    y = table.define("y")
    assert y == Symbol("y", GLOBALSCOPE, 1)


def test_resolve_global():
    table = SymbolTable()
    x = table.define("x")
    y = table.define("y")

    assert table.resolve("x") == (True, Symbol("x", GLOBALSCOPE, 0))
    assert table.resolve("y") == (True, Symbol("y", GLOBALSCOPE, 1))


def test_resolve_local():
    global_table = SymbolTable()
    x = global_table.define("a")
    y = global_table.define("b")

    local_table = SymbolTable(global_table)
    x = local_table.define("c")
    y = local_table.define("d")

    assert global_table.resolve("a") == (True, Symbol("a", GLOBALSCOPE, 0))
    assert global_table.resolve("b") == (True, Symbol("b", GLOBALSCOPE, 1))

    assert local_table.resolve("a") == (True, Symbol("a", GLOBALSCOPE, 0))
    assert local_table.resolve("b") == (True, Symbol("b", GLOBALSCOPE, 1))
    assert local_table.resolve("c") == (True, Symbol("c", LOCALSCOPE, 0))
    assert local_table.resolve("d") == (True, Symbol("d", LOCALSCOPE, 1))


def test_nested_resolve_local():
    global_table = SymbolTable()
    x = global_table.define("a")
    y = global_table.define("b")

    local_table_1 = SymbolTable(global_table)
    x = local_table_1.define("c")
    y = local_table_1.define("d")

    local_table_2 = SymbolTable(local_table_1)
    x = local_table_2.define("e")
    y = local_table_2.define("f")

    assert global_table.resolve("a") == (True, Symbol("a", GLOBALSCOPE, 0))
    assert global_table.resolve("b") == (True, Symbol("b", GLOBALSCOPE, 1))

    assert local_table_1.resolve("a") == (True, Symbol("a", GLOBALSCOPE, 0))
    assert local_table_1.resolve("b") == (True, Symbol("b", GLOBALSCOPE, 1))
    assert local_table_1.resolve("c") == (True, Symbol("c", LOCALSCOPE, 0))
    assert local_table_1.resolve("d") == (True, Symbol("d", LOCALSCOPE, 1))

    assert local_table_2.resolve("a") == (True, Symbol("a", GLOBALSCOPE, 0))
    assert local_table_2.resolve("b") == (True, Symbol("b", GLOBALSCOPE, 1))
    assert local_table_2.resolve("e") == (True, Symbol("e", LOCALSCOPE, 0))
    assert local_table_2.resolve("f") == (True, Symbol("f", LOCALSCOPE, 1))


def test_resolve_builtin():
    global_table = SymbolTable()
    x = global_table.define("a")
    y = global_table.define("b")

    local_table_1 = SymbolTable(global_table)
    x = local_table_1.define("c")
    y = local_table_1.define("d")

    local_table_2 = SymbolTable(local_table_1)
    x = local_table_2.define("e")
    y = local_table_2.define("f")

    global_table.define_builtin(0, "x")
    global_table.define_builtin(1, "y")
    global_table.define_builtin(2, "z")

    assert local_table_2.resolve("x") == (True, Symbol("x", BUILTINSCOPE, 0))
    assert local_table_2.resolve("y") == (True, Symbol("y", BUILTINSCOPE, 1))
    assert local_table_2.resolve("z") == (True, Symbol("z", BUILTINSCOPE, 2))
