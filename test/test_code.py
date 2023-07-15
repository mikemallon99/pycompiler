from pycompiler.code import Opcode, Instructions, make

def test_make_constant():
    instruction: Instructions = make(Opcode.CONSTANT, [65534])
    assert instruction[0] == Opcode.CONSTANT.value
    assert instruction[1:] == (65534).to_bytes(2, byteorder='big')
