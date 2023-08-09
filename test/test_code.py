from pycompiler.code import Opcode, Instructions, make, instructions_to_str

def test_make_constant():
    instruction: Instructions = make(Opcode.CONSTANT, [65534])
    assert instruction[0] == Opcode.CONSTANT.value
    assert instruction[1:] == (65534).to_bytes(2, byteorder='big')

def test_instr_strings():
    instructions: List[Instructions] = [
        make(Opcode.CONSTANT, [1]),
        make(Opcode.CONSTANT, [2]),
        make(Opcode.CONSTANT, [65535]),
    ]

    expected = (
        "0000 CONSTANT 1\n"
        "0003 CONSTANT 2\n"
        "0006 CONSTANT 65535\n"
    )

    concatted: Instructions = bytearray()
    for ins in instructions:
        concatted += ins

    assert instructions_to_str(concatted) == expected
