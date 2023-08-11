import builtins
from typing import List, Any

from pycompiler.compiler import Compiler
from pycompiler.vm import VM
from pycompiler.code import make, Opcode, Instructions, instructions_to_str
from pycompiler.objects import Object, IntObject, BooleanObject, NullObject
from pycompiler.parser import Parser
from pycompiler.lexer import Lexer

def pytest_assertrepr_compare(op, left, right):
    if isinstance(left, Instructions) and isinstance(right, Instructions) and op == "==":
        return [
            "Instructions differ:",
            "   vals: {} != {}".format(instructions_to_str(left), instructions_to_str(right)),
        ]

def run_vm_test(
            test_prog: str, 
            exp_obj: Object
        ):
    ast: List[Statement] = Parser(Lexer(test_prog)).parse()
    compiler = Compiler()
    compiler.compile(ast)
    vm = VM(compiler.bytecode())
    vm.run()
    assert vm.last_popped() == exp_obj


def test_integer_arithmetic():
    run_vm_test(
        "1",
        IntObject(1)
    )
    run_vm_test(
        "2",
        IntObject(2)
    )
    run_vm_test(
        "1 + 2",
        IntObject(3)
    )
    run_vm_test(
        "6 - 2",
        IntObject(4)
    )
    run_vm_test(
        "5 * 4",
        IntObject(20)
    )
    run_vm_test(
        "4 / 2",
        IntObject(2)
    )

    run_vm_test(
        "5 * 4 * 2 * 3",
        IntObject(120)
    )
    run_vm_test(
        "5 + 4 * (2 - 3)",
        IntObject(1)
    )

def test_boolean():
    run_vm_test(
        "true",
        BooleanObject(True)
    )
    run_vm_test(
        "false",
        BooleanObject(False)
    )

def test_comparison():
    run_vm_test(
        "1 == 2",
        BooleanObject(False)
    )
    run_vm_test(
        "5 == 5",
        BooleanObject(True)
    )
    run_vm_test(
        "1 != 2",
        BooleanObject(True)
    )
    run_vm_test(
        "5 != 5",
        BooleanObject(False)
    )
    run_vm_test(
        "true != true",
        BooleanObject(False)
    )
    run_vm_test(
        "false == false",
        BooleanObject(True)
    )
    run_vm_test(
        "1 < 2",
        BooleanObject(True)
    )
    run_vm_test(
        "1 > 2",
        BooleanObject(False)
    )
    run_vm_test(
        "2 > 1",
        BooleanObject(True)
    )
    run_vm_test(
        "2 < 1",
        BooleanObject(False)
    )

def test_prefix():
    run_vm_test(
        "-5",
        IntObject(-5)
    )
    run_vm_test(
        "-5 + 10",
        IntObject(5)
    )
    run_vm_test(
        "!true",
        BooleanObject(False)
    )
    run_vm_test(
        "!(2 > 3)",
        BooleanObject(True)
    )

def test_prefix():
    run_vm_test(
        "if (true) {10}",
        IntObject(10)
    )
    run_vm_test(
        "if (true) {10} else {20}",
        IntObject(10)
    )
    run_vm_test(
        "if (false) {10} else {20}; 30",
        IntObject(30)
    )
    run_vm_test(
        "if (true) {10} else {20}; 30",
        IntObject(30)
    )
    run_vm_test(
        "if (1 < 2) {10} else {20}",
        IntObject(10)
    )
    run_vm_test(
        "if (false) {10}",
        NullObject()
    )

