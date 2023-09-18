from pycompiler.code import (
    Opcode,
    Instructions,
    make,
    instructions_to_str,
    read_operands,
    lookup_opcode,
)


def test_make_constant():
    instruction: Instructions = make(Opcode.CONSTANT, [65534])
    assert instruction[0] == Opcode.CONSTANT.value
    assert instruction[1:] == (65534).to_bytes(2, byteorder="big")


def test_make_getlocal():
    instruction: Instructions = make(Opcode.GETLOCAL, [255])
    assert instruction[0] == Opcode.GETLOCAL.value
    assert instruction[1:] == (255).to_bytes(1, byteorder="big")


def test_make_add():
    instruction: Instructions = make(Opcode.ADD, [])
    assert instruction[0] == Opcode.ADD.value
    assert instruction[1:] == bytearray()


def test_make_closure():
    instruction: Instructions = make(Opcode.CLOSURE, [65534, 255])
    assert instruction[0] == Opcode.CLOSURE.value
    assert instruction[1:3] == (65534).to_bytes(2, byteorder="big")
    assert instruction[3:] == (255).to_bytes(1, byteorder="big")


def test_instr_strings():
    instructions: List[Instructions] = [
        make(Opcode.ADD, []),
        make(Opcode.CONSTANT, [2]),
        make(Opcode.CONSTANT, [65535]),
        make(Opcode.GETLOCAL, [255]),
        make(Opcode.CLOSURE, [65534, 255]),
    ]

    expected = "0000 ADD\n" "0001 CONSTANT 2\n" "0004 CONSTANT 65535\n" "0007 GETLOCAL 255\n" "0009 CLOSURE 65534 255\n"

    concatted: Instructions = bytearray()
    for ins in instructions:
        concatted += ins

    assert instructions_to_str(concatted) == expected


# For decoding an instruction
def test_read_operands():
    instruction = make(Opcode.CONSTANT, [65535])
    opcode = lookup_opcode(instruction[0])
    operands, bytes_read = read_operands(opcode, instruction[1:])
    assert operands == [65535]
    assert bytes_read == 2
