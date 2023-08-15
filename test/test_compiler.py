import builtins
from typing import List, Any

from pycompiler.compiler import Compiler
from pycompiler.code import make, Opcode, Instructions, instructions_to_str
from pycompiler.objects import Object, IntObject, StringObject, CompiledFunctionObject, NullObject
from pycompiler.parser import Parser, Statement
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


def compare_consts(left_consts, right_consts):
    for left_const, right_const in zip(left_consts, right_consts):
        if isinstance(left_const, CompiledFunctionObject) and isinstance(right_const, CompiledFunctionObject):
            compare_insts(left_const.value, right_const.value)
        elif isinstance(left_const, NullObject) and isinstance(right_const, NullObject):
            assert True
        else:
            assert left_const.value == right_const.value


def concat_insts(insts: List[Instructions]) -> Instructions:
    output = bytearray()
    for ins in insts:
        output += ins
    return output


def run_compiler_test(
    test_prog: str, exp_consts: List[Any], exp_insts_list: List[Instructions]
):
    # Convert const values to objects
    const_objects: List[Object] = []
    for exp_const in exp_consts:
        if isinstance(exp_const, Instructions):
            const_objects.append(CompiledFunctionObject(exp_const))
        elif isinstance(exp_const, builtins.int):
            const_objects.append(IntObject(exp_const))
        elif isinstance(exp_const, builtins.str):
            const_objects.append(StringObject(exp_const))
        else:
            raise Exception(f"Cannot convert type to object: {type(exp_const)}")

    ast: List[Statement] = Parser(Lexer(test_prog)).parse()
    compiler = Compiler()
    compiler.compile(ast)

    exp_insts_code = concat_insts(exp_insts_list)

    instructions, constants = compiler.bytecode()
    compare_insts(instructions, exp_insts_code)
    compare_consts(constants, const_objects)


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


def test_functions():
    run_compiler_test(
        "fn() { return 5 + 10 }",
        [
            5,
            10,
            concat_insts(
                [
                    make(Opcode.CONSTANT, [0]),
                    make(Opcode.CONSTANT, [1]),
                    make(Opcode.ADD, []),
                    make(Opcode.RETURNVALUE, []),
                ]
            ),
        ],
        [
            make(Opcode.CONSTANT, [2]),
            make(Opcode.POP, []),
        ],
    )
    run_compiler_test(
        "fn() { 5 + 10 }",
        [
            5,
            10,
            concat_insts(
                [
                    make(Opcode.CONSTANT, [0]),
                    make(Opcode.CONSTANT, [1]),
                    make(Opcode.ADD, []),
                    make(Opcode.RETURNVALUE, []),
                ]
            ),
        ],
        [
            make(Opcode.CONSTANT, [2]),
            make(Opcode.POP, []),
        ],
    )
    run_compiler_test(
        "fn() { 5; 10 }",
        [
            5,
            10,
            concat_insts(
                [
                    make(Opcode.CONSTANT, [0]),
                    make(Opcode.POP, []),
                    make(Opcode.CONSTANT, [1]),
                    make(Opcode.RETURNVALUE, []),
                ]
            ),
        ],
        [
            make(Opcode.CONSTANT, [2]),
            make(Opcode.POP, []),
        ],
    )
    run_compiler_test(
        "fn() { }",
        [
            concat_insts(
                [
                    make(Opcode.RETURN, []),
                ]
            ),
        ],
        [
            make(Opcode.CONSTANT, [0]),
            make(Opcode.POP, []),
        ],
    )


def test_scopes():
    compiler = Compiler()
    assert compiler.scope_index == 0

    compiler._emit(Opcode.MUL, [])

    compiler._enter_scope()
    assert compiler.scope_index == 1

    compiler._emit(Opcode.SUB, [])
    assert len(compiler.scopes[compiler.scope_index].instructions) == 1

    compiler._leave_scope()
    assert compiler.scope_index == 0

    compiler._emit(Opcode.ADD, [])
    assert len(compiler.scopes[compiler.scope_index].instructions) == 2

    assert compiler.scopes[compiler.scope_index].last_ins.opcode == Opcode.ADD
    assert compiler.scopes[compiler.scope_index].prev_ins.opcode == Opcode.MUL


def test_calls():
    run_compiler_test(
        "fn() { 24 }()",
        [
            24,
            concat_insts(
                [
                    make(Opcode.CONSTANT, [0]),
                    make(Opcode.RETURNVALUE, []),
                ]
            ),
        ],
        [
            make(Opcode.CONSTANT, [1]),
            make(Opcode.CALL, []),
            make(Opcode.POP, []),
        ],
    )
    run_compiler_test(
        "let no_arg = fn() { 24 }; no_arg()",
        [
            24,
            concat_insts(
                [
                    make(Opcode.CONSTANT, [0]),
                    make(Opcode.RETURNVALUE, []),
                ]
            ),
        ],
        [
            make(Opcode.CONSTANT, [1]),
            make(Opcode.SETGLOBAL, [0]),
            make(Opcode.GETGLOBAL, [0]),
            make(Opcode.CALL, []),
            make(Opcode.POP, []),
        ],
    )