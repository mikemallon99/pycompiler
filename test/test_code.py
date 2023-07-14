from pycompiler.code import Opcode, Instruction, make

def test_make_constant():
    instruction: Instruction = make(Opcode.CONSTANT, [65534])
    assert instruction.encoding[0] == Opcode.CONSTANT.value
    assert instruction.encoding[1:] == (65534).to_bytes(2, byteorder='big')
