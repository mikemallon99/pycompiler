import builtins
from typing import List, Any

from pycompiler.compiler import Compiler
from pycompiler.vm import VM
from pycompiler.code import make, Opcode, Instructions, instructions_to_str
from pycompiler.objects import Object, IntObject
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
    bytecode = compiler.compile(ast)
    vm = VM(bytecode)
    vm.run()
    assert vm.stack_top() == exp_obj


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

