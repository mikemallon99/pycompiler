from typing import List, Tuple, Any
from enum import Enum, auto


class Opcode(Enum):
    CONSTANT = auto()
    TRUE = auto()
    FALSE = auto()
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    POP = auto()
    EQUAL = auto()
    NOTEQUAL = auto()
    GREATERTHAN = auto()
    MINUS = auto()
    BANG = auto()
    NULL = auto()


Instructions = bytearray

def instructions_to_str(instructions: Instructions) -> str:
    out_string: str = ""

    i: int = 0
    while i < len(instructions):
        op: Opcode = lookup_opcode(instructions[i])
        out_string += "{:04X}".format(i)
        out_string += f" {op.name}"

        operands, read = read_operands(op, instructions[i+1:])
        for operand in operands:
            out_string += f" {operand}"

        out_string += "\n"
        i += 1 + read

    return out_string


def lookup_opcode(op_bytes: bytes) -> Opcode:
    op = Opcode.NULL
    for member in Opcode:
        if op_bytes == member.value:
            op = member
            break
    return op


def read_operands(op: Opcode, operands: bytearray) -> Tuple[List[int], int]:
    match op:
        case Opcode.CONSTANT:
            return [int.from_bytes(operands[0:2], byteorder='big')], 2
        case _:
            return [], 0


def make(op: Opcode, operands: List[int]=[]) -> Instructions:
    instruction: bytearray = bytearray(1)
    instruction[0] = op.value

    match op:
        case Opcode.CONSTANT:
            instruction += bytearray(2)
            instruction[1:] = operands[0].to_bytes(2, byteorder='big')

    return instruction


