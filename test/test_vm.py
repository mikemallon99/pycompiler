import builtins
from typing import List, Any

from pycompiler.compiler import Compiler
from pycompiler.vm import VM
from pycompiler.code import make, Opcode, Instructions, instructions_to_str
from pycompiler.objects import (
    Object,
    IntObject,
    BooleanObject,
    NullObject,
    StringObject,
    ArrayObject,
    MapObject,
)
from pycompiler.parser import Parser, Statement
from pycompiler.lexer import Lexer


def pytest_assertrepr_compare(op, left, right):
    if (
        isinstance(left, Instructions)
        and isinstance(right, Instructions)
        and op == "=="
    ):
        return [
            "Instructions differ:",
            "   vals: {} != {}".format(
                instructions_to_str(left), instructions_to_str(right)
            ),
        ]


def run_vm_test(test_prog: str, exp_obj: Object | str):
    ast: List[Statement] = Parser(Lexer(test_prog)).parse()
    compiler = Compiler()
    compiler.compile(ast)
    vm = VM(compiler.bytecode())
    err = vm.run()
    if err:
        assert err == exp_obj
        return
    assert vm.last_popped() == exp_obj


def test_integer_arithmetic():
    run_vm_test("1", IntObject(1))
    run_vm_test("2", IntObject(2))
    run_vm_test("1 + 2", IntObject(3))
    run_vm_test("6 - 2", IntObject(4))
    run_vm_test("5 * 4", IntObject(20))
    run_vm_test("4 / 2", IntObject(2))

    run_vm_test("5 * 4 * 2 * 3", IntObject(120))
    run_vm_test("5 + 4 * (2 - 3)", IntObject(1))


def test_boolean():
    run_vm_test("true", BooleanObject(True))
    run_vm_test("false", BooleanObject(False))
    run_vm_test("!(if (false) {5})", BooleanObject(True))


def test_comparison():
    run_vm_test("1 == 2", BooleanObject(False))
    run_vm_test("5 == 5", BooleanObject(True))
    run_vm_test("1 != 2", BooleanObject(True))
    run_vm_test("5 != 5", BooleanObject(False))
    run_vm_test("true != true", BooleanObject(False))
    run_vm_test("false == false", BooleanObject(True))
    run_vm_test("1 < 2", BooleanObject(True))
    run_vm_test("1 > 2", BooleanObject(False))
    run_vm_test("2 > 1", BooleanObject(True))
    run_vm_test("2 < 1", BooleanObject(False))


def test_prefix():
    run_vm_test("-5", IntObject(-5))
    run_vm_test("-5 + 10", IntObject(5))
    run_vm_test("!true", BooleanObject(False))
    run_vm_test("!(2 > 3)", BooleanObject(True))


def test_if_else():
    run_vm_test("if (true) {10}", IntObject(10))
    run_vm_test("if (true) {10} else {20}", IntObject(10))
    run_vm_test("if (false) {10} else {20}; 30", IntObject(30))
    run_vm_test("if (true) {10} else {20}; 30", IntObject(30))
    run_vm_test("if (1 < 2) {10} else {20}", IntObject(10))
    run_vm_test("if (false) {10}", NullObject())


def test_globals():
    run_vm_test("let x = 2; x", IntObject(2))
    run_vm_test("let x = 2; let y = 3; y;", IntObject(3))
    run_vm_test("let x = 2; let y = x; y;", IntObject(2))
    run_vm_test("let x = 2; let y = 3; x + y", IntObject(5))
    run_vm_test("let x = 2; let y = x + x; x + y", IntObject(6))


def test_string():
    run_vm_test('"test"', StringObject("test"))
    run_vm_test('"one" + "two"', StringObject("onetwo"))


def test_array():
    run_vm_test("[]", ArrayObject([]))
    run_vm_test("[1 + 2, 3 + 4]", ArrayObject([IntObject(3), IntObject(7)]))
    run_vm_test(
        '[5, "test", 3 * 10]',
        ArrayObject([IntObject(5), StringObject("test"), IntObject(30)]),
    )


def test_map():
    run_vm_test("{}", MapObject({}))
    run_vm_test(
        "{1 + 1: 1 + 2, 3 + 3: 3 + 4}",
        MapObject({IntObject(2): IntObject(3), IntObject(6): IntObject(7)}),
    )


def test_index():
    run_vm_test("[1, 2, 3][1 + 1]", IntObject(3))
    run_vm_test("{1 + 1: 1 + 2, 3 + 3: 3 + 4}[6]", IntObject(7))
    run_vm_test("[1, 2, 3][3]", NullObject())
    run_vm_test("[1, 2, 3][-1]", NullObject())
    run_vm_test("{1 + 1: 1 + 2, 3 + 3: 3 + 4}[1]", NullObject())
    run_vm_test('{1 + 1: 1 + 2, 3 + 3: 3 + 4}["yo"]', NullObject())

def test_fn_no_args():
    run_vm_test(
        "let test = fn () { 5 + 10 }; test()",
        IntObject(15),
    )
    run_vm_test(
        "let test = fn () { }; test()",
        NullObject(),
    )
    run_vm_test(
        "let one = fn () { 1 }; let two = fn() {2}; two()",
        IntObject(2),
    )
    run_vm_test(
        "let one = fn () { 1 }; let two = fn() {2}; two(); two()",
        IntObject(2),
    )
    run_vm_test(
        "let one = fn () { 1 }; let two = fn() {2}; two() + two()",
        IntObject(4),
    )
    run_vm_test(
        "let one = fn () { 1 }; let two = fn() {2}; one() + two()",
        IntObject(3),
    )
    run_vm_test(
        "let one = fn () { 1 }; let two = fn() { one() + one() }; two() * two()",
        IntObject(4),
    )
    run_vm_test(
        "let one = fn () { return 99; 100 }; one()",
        IntObject(99),
    )
    run_vm_test(
        "let one = fn () { return 99; return 100 }; one()",
        IntObject(99),
    )
    run_vm_test(
        "let one = fn () { }; let two = fn () { one() }; two()",
        NullObject(),
    )
    # First class function
    run_vm_test(
        "let one = fn () { 1 }; let two = fn () { one }; two()()",
        IntObject(1),
    )


def test_fn_local_bindings():
    run_vm_test(
        "let test = fn () { let a = 5; a }; test()",
        IntObject(5),
    )
    run_vm_test(
        "let onetwo = fn () { let a = 1; let b = 2; a + b }; onetwo()",
        IntObject(3),
    )
    run_vm_test(
        "let onetwo = fn () { let a = 1; let b = 2; a + b }; let threefour = fn () { let c = 3; let d = 4; c + d }; onetwo() + threefour()",
        IntObject(10),
    )
    run_vm_test(
        "let global_num = 100; let test = fn () { let a = 5; global_num - a }; test()",
        IntObject(95),
    )


def test_fn_args():
    run_vm_test(
        "let test = fn (a) { a; }; test(5)",
        IntObject(5),
    )
    run_vm_test(
        "let test = fn (a, b) { a + b; }; test(5, 6)",
        IntObject(11),
    )
    run_vm_test(
    """
        let globalNum = 10;

        let sum = fn(a, b) {
            let c = a + b;
            c + globalNum;
        };

        let outer = fn() {
            sum(1, 2) + sum(3, 4) + globalNum;
        };

        outer() + globalNum;
    """,
        IntObject(50),
    )
    run_vm_test(
        "fn () { }(1)",
        "wrong number of args: want 0, got 1",
    )
    run_vm_test(
        "fn (a) { a; }()",
        "wrong number of args: want 1, got 0",
    )
    run_vm_test(
        "fn (a, b) { a + b; }(1)",
        "wrong number of args: want 2, got 1",
    )
