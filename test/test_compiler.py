import builtins
from typing import List, Any

from pycompiler.compiler import Compiler
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

def run_compiler_test(
            test_prog: str, 
            exp_consts: List[Any], 
            exp_insts: List[Instructions]
        ):
    concat_insts = bytearray()
    for ins in exp_insts:
        concat_insts += ins
    
    # Convert const values to objects
    const_objects: List[Objects] = []
    for exp_const in exp_consts:
        match type(exp_const):
            case builtins.int:
                const_objects.append(IntObject(exp_const))
            case _:
                raise Exception(f"Cannot convert type to object: {type(exp_const)}")

    ast: List[Statement] = Parser(Lexer(test_prog)).parse()
    compiler = Compiler()
    compiler.compile(ast)

    assert compiler.instructions == concat_insts
    assert compiler.constants == const_objects

def test_integer_arithmetic():
    run_compiler_test(
        "1 + 2",
        [1, 2],
        [
            make(Opcode.CONSTANT, [0]),
            make(Opcode.CONSTANT, [1])
        ]
    )

