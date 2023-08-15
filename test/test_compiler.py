import builtins
from typing import List, Any

from pycompiler.compiler import Compiler
from pycompiler.code import make, Opcode, Instructions, instructions_to_str
from pycompiler.objects import Object, IntObject, StringObject
from pycompiler.parser import Parser
from pycompiler.lexer import Lexer


def pytest_assertrepr_compare(op, left, right):
    if isinstance(left, bytearray) and isinstance(right, bytearray) and op == "==":
        return [
            "Instructions differ:",
            "   vals: {} != {}".format(
                instructions_to_str(left), instructions_to_str(right)
            ),
        ]


def compare_insts(left, right):
    assert instructions_to_str(left) == instructions_to_str(right)


def run_compiler_test(
    test_prog: str, exp_consts: List[Any], exp_insts: List[Instructions]
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
            case builtins.str:
                const_objects.append(StringObject(exp_const))
            case _:
                raise Exception(f"Cannot convert type to object: {type(exp_const)}")

    ast: List[Statement] = Parser(Lexer(test_prog)).parse()
    compiler = Compiler()
    compiler.compile(ast)

    compare_insts(compiler.instructions, concat_insts)
    assert compiler.constants == const_objects


def test_integer_arithmetic():
    run_compiler_test(
        "1 + 2",
        [1, 2],
        [
            make(Opcode.CONSTANT, [0]),
            make(Opcode.CONSTANT, [1]),
            make(Opcode.ADD, []),
            make(Opcode.POP, []),
        ],
    )

    run_compiler_test(
        "1 - 2",
        [1, 2],
        [
            make(Opcode.CONSTANT, [0]),
            make(Opcode.CONSTANT, [1]),
            make(Opcode.SUB, []),
            make(Opcode.POP, []),
        ],
    )

    run_compiler_test(
        "1 * 2",
        [1, 2],
        [
            make(Opcode.CONSTANT, [0]),
            make(Opcode.CONSTANT, [1]),
            make(Opcode.MUL, []),
            make(Opcode.POP, []),
        ],
    )

    run_compiler_test(
        "1 / 2",
        [1, 2],
        [
            make(Opcode.CONSTANT, [0]),
            make(Opcode.CONSTANT, [1]),
            make(Opcode.DIV, []),
            make(Opcode.POP, []),
        ],
    )


def test_boolean():
    run_compiler_test(
        "true",
        [],
        [
            make(Opcode.TRUE, []),
            make(Opcode.POP, []),
        ],
    )

    run_compiler_test(
        "false",
        [],
        [
            make(Opcode.FALSE, []),
            make(Opcode.POP, []),
        ],
    )


def test_comparisons():
    run_compiler_test(
        "1 == 2",
        [1, 2],
        [
            make(Opcode.CONSTANT, [0]),
            make(Opcode.CONSTANT, [1]),
            make(Opcode.EQUAL, []),
            make(Opcode.POP, []),
        ],
    )

    run_compiler_test(
        "1 != 2",
        [1, 2],
        [
            make(Opcode.CONSTANT, [0]),
            make(Opcode.CONSTANT, [1]),
            make(Opcode.NOTEQUAL, []),
            make(Opcode.POP, []),
        ],
    )

    run_compiler_test(
        "1 > 2",
        [1, 2],
        [
            make(Opcode.CONSTANT, [0]),
            make(Opcode.CONSTANT, [1]),
            make(Opcode.GREATERTHAN, []),
            make(Opcode.POP, []),
        ],
    )

    run_compiler_test(
        "1 < 2",
        [2, 1],
        [
            make(Opcode.CONSTANT, [0]),
            make(Opcode.CONSTANT, [1]),
            make(Opcode.GREATERTHAN, []),
            make(Opcode.POP, []),
        ],
    )


def test_prefixes():
    run_compiler_test(
        "-1",
        [1],
        [
            make(Opcode.CONSTANT, [0]),
            make(Opcode.MINUS, []),
            make(Opcode.POP, []),
        ],
    )

    run_compiler_test(
        "!true",
        [],
        [
            make(Opcode.TRUE, []),
            make(Opcode.BANG, []),
            make(Opcode.POP, []),
        ],
    )


def test_jumps():
    run_compiler_test(
        "if (true) {5}; 3333;",
        [5, 3333],
        [
            # 0000
            make(Opcode.TRUE, []),
            # 0001
            make(Opcode.JUMPCOND, [10]),
            # 0004
            make(Opcode.CONSTANT, [0]),
            # 0007
            make(Opcode.JUMP, [11]),
            # 0010
            make(Opcode.NULL, []),
            # 0011
            make(Opcode.POP, []),
            # 0012
            make(Opcode.CONSTANT, [1]),
            # 0015
            make(Opcode.POP, []),
        ],
    )

    run_compiler_test(
        "if (false) {5} else {10}; 3333;",
        [5, 10, 3333],
        [
            # 0000
            make(Opcode.FALSE, []),
            # 0001
            make(Opcode.JUMPCOND, [10]),
            # 0004
            make(Opcode.CONSTANT, [0]),
            # 0007
            make(Opcode.JUMP, [13]),
            # 0010
            make(Opcode.CONSTANT, [1]),
            # 0013
            make(Opcode.POP, []),
            # 0014
            make(Opcode.CONSTANT, [2]),
            # 0017
            make(Opcode.POP, []),
        ],
    )


def test_let():
    run_compiler_test(
        "let x = 2; let y = 3;",
        [2, 3],
        [
            make(Opcode.CONSTANT, [0]),
            make(Opcode.SETGLOBAL, [0]),
            make(Opcode.CONSTANT, [1]),
            make(Opcode.SETGLOBAL, [1]),
        ],
    )
    run_compiler_test(
        "let x = 2; x;",
        [2],
        [
            make(Opcode.CONSTANT, [0]),
            make(Opcode.SETGLOBAL, [0]),
            make(Opcode.GETGLOBAL, [0]),
            make(Opcode.POP, []),
        ],
    )
    run_compiler_test(
        "let x = 2; let y = x; y;",
        [2],
        [
            make(Opcode.CONSTANT, [0]),
            make(Opcode.SETGLOBAL, [0]),
            make(Opcode.GETGLOBAL, [0]),
            make(Opcode.SETGLOBAL, [1]),
            make(Opcode.GETGLOBAL, [1]),
            make(Opcode.POP, []),
        ],
    )


def test_string():
    run_compiler_test(
        '"monkey"',
        ["monkey"],
        [
            make(Opcode.CONSTANT, [0]),
            make(Opcode.POP, []),
        ],
    )
    run_compiler_test(
        '"mon" + "key"',
        ["mon", "key"],
        [
            make(Opcode.CONSTANT, [0]),
            make(Opcode.CONSTANT, [1]),
            make(Opcode.ADD, []),
            make(Opcode.POP, []),
        ],
    )


def test_array():
    run_compiler_test(
        "[]",
        [],
        [
            make(Opcode.ARRAY, [0]),
            make(Opcode.POP, []),
        ],
    )
    run_compiler_test(
        "[1 + 2, 3 + 4]",
        [1, 2, 3, 4],
        [
            make(Opcode.CONSTANT, [0]),
            make(Opcode.CONSTANT, [1]),
            make(Opcode.ADD, []),
            make(Opcode.CONSTANT, [2]),
            make(Opcode.CONSTANT, [3]),
            make(Opcode.ADD, []),
            make(Opcode.ARRAY, [2]),
            make(Opcode.POP, []),
        ],
    )


def test_map():
    run_compiler_test(
        "{}",
        [],
        [
            make(Opcode.MAP, [0]),
            make(Opcode.POP, []),
        ],
    )
    run_compiler_test(
        "{1 + 1: 1 + 2, 3 + 3: 3 + 4}",
        [1, 1, 1, 2, 3, 3, 3, 4],
        [
            make(Opcode.CONSTANT, [0]),
            make(Opcode.CONSTANT, [1]),
            make(Opcode.ADD, []),
            make(Opcode.CONSTANT, [2]),
            make(Opcode.CONSTANT, [3]),
            make(Opcode.ADD, []),
            make(Opcode.CONSTANT, [4]),
            make(Opcode.CONSTANT, [5]),
            make(Opcode.ADD, []),
            make(Opcode.CONSTANT, [6]),
            make(Opcode.CONSTANT, [7]),
            make(Opcode.ADD, []),
            make(Opcode.MAP, [2]),
            make(Opcode.POP, []),
        ],
    )


def test_index():
    run_compiler_test(
        "[1, 2, 3][1 + 1]",
        [1, 2, 3, 1, 1],
        [
            make(Opcode.CONSTANT, [0]),
            make(Opcode.CONSTANT, [1]),
            make(Opcode.CONSTANT, [2]),
            make(Opcode.ARRAY, [3]),
            make(Opcode.CONSTANT, [3]),
            make(Opcode.CONSTANT, [4]),
            make(Opcode.ADD, []),
            make(Opcode.INDEX, []),
            make(Opcode.POP, []),
        ],
    )
