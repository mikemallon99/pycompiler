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
    JUMPCOND = auto()
    JUMP = auto()
    GETGLOBAL = auto()
    SETGLOBAL = auto()
    GETLOCAL = auto()
    SETLOCAL = auto()
    GETBUILTIN = auto()
    GETFREE = auto()
    ARRAY = auto()
    MAP = auto()
    INDEX = auto()
    CALL = auto()
    RETURNVALUE = auto()
    RETURN = auto()
    CLOSURE = auto()
    CURRENTCLOSURE = auto()
    NULL = auto()


Instructions = bytearray


def instructions_to_str(instructions: Instructions) -> str:
    out_string: str = ""

    i: int = 0
    while i < len(instructions):
        op: Opcode = lookup_opcode(instructions[i])
        out_string += "{:04X}".format(i)
        out_string += f" {op.name}"

        operands, read = read_operands(op, instructions[i + 1 :])
        for operand in operands:
            out_string += f" {operand}"

        out_string += "\n"
        i += 1 + read

    return out_string


def lookup_opcode(op_bytes: int) -> Opcode:
    op = Opcode.NULL
    for member in Opcode:
        if op_bytes == member.value:
            op = member
            break
    return op


def read_operands(op: Opcode, operands: bytearray) -> Tuple[List[int], int]:
    if (
        op == Opcode.CONSTANT
        or op == Opcode.JUMPCOND
        or op == Opcode.JUMP
        or op == Opcode.GETGLOBAL
        or op == Opcode.SETGLOBAL
        or op == Opcode.ARRAY
        or op == Opcode.MAP
    ):
        return [int.from_bytes(operands[0:2], byteorder="big")], 2
    elif (
        op == Opcode.GETLOCAL
        or op == Opcode.SETLOCAL
        or op == Opcode.GETBUILTIN
        or op == Opcode.GETFREE
        or op == Opcode.CALL
    ):
        return [int.from_bytes(operands[0:1], byteorder="big")], 1
    elif op == Opcode.CLOSURE:
        return [int.from_bytes(operands[0:2], byteorder="big"), int.from_bytes(operands[2:3], byteorder="big")], 3
    else:
        return [], 0


def make(op: Opcode, operands: List[int] = []) -> Instructions:
    instruction: bytearray = bytearray(1)
    instruction[0] = op.value

    if (
        op == Opcode.CONSTANT
        or op == Opcode.JUMPCOND
        or op == Opcode.JUMP
        or op == Opcode.GETGLOBAL
        or op == Opcode.SETGLOBAL
        or op == Opcode.ARRAY
        or op == Opcode.MAP
    ):
        instruction += bytearray(2)
        instruction[1:] = operands[0].to_bytes(2, byteorder="big")
    elif (
        op == Opcode.GETLOCAL
        or op == Opcode.SETLOCAL
        or op == Opcode.GETBUILTIN
        or op == Opcode.GETFREE
        or op == Opcode.CALL
    ):
        instruction += bytearray(1)
        instruction[1:] = operands[0].to_bytes(1, byteorder="big")
    elif op == Opcode.CLOSURE:
        instruction += bytearray(3)
        instruction[1:3] = operands[0].to_bytes(2, byteorder="big")
        instruction[3:] = operands[1].to_bytes(1, byteorder="big")

    return instruction
