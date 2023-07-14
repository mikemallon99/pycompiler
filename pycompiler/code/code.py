from typing import List, Tuple, Any
from enum import Enum, auto


class Opcode(Enum):
    CONSTANT = auto()
    NULL = auto()


class Instruction:
    def __init__(self, encoding: bytearray):
        self.encoding: bytearray = encoding

    def __eq__(self, other: Any):
        if not isinstance(other, Instruction):
            return NotImplemented
        return self.encoding == other.encoding

    def __str__(self) -> str:
        op = Opcode.NULL
        for member in Opcode:
            if self.encoding[0] == member.value:
                op = member
                break

        # Convert from encoding back into operands
        operands: List[int] = []
        match op:
            case Opcode.CONSTANT:
                operands = [int.from_bytes(self.encoding[1:], byteorder='big')]

        out_string: str = op.name
        for operand in operands:
            out_string += f" {operand}"
        return out_string

    def __repr__(self):
        return f"Instruction: {self.__str__()}"


def make(op: Opcode, operands: List[int]=[]) -> Instruction:
    instruction: bytearray = bytearray(1)
    instruction[0] = op.value

    match op:
        case Opcode.CONSTANT:
            instruction += bytearray(2)
            instruction[1:] = operands[0].to_bytes(2, byteorder='big')

    return Instruction(instruction)
