from typing import List, Tuple
from pycompiler.objects import (
    Object,
    IntObject
)
from pycompiler.code import Instruction, Opcode, make
from pycompiler.parser import (
    Statement, 
    LetStatement,
    ReturnStatement,
    ExpressionStatement,
    Expression,
    LiteralExpression,
    InfixExpression,
    PrefixExpression,
    Literal,
    IntLiteral
)

Bytecode = Tuple[List[Instruction], List[Object]]

class Compiler:
    def __init__(self):
        self.instructions: List[Instruction] = []
        self.constants: List[Object] = []

    def compile(self, ast: List[Statement]):
        for statement in ast:
            match statement:
                case ExpressionStatement():
                    self._compile_expression(statement.expr)
                case _:
                    raise NotImplemented

        return [], []

    def _compile_expression(self, expression: Expression):
        match expression:
            case LiteralExpression():
                self._compile_literal(expression.literal)
            case PrefixExpression():
                self._compile_expression(expression.right)
            case InfixExpression():
                self._compile_expression(expression.left)
                self._compile_expression(expression.right)
            case _:
                raise NotImplemented

    def _compile_literal(self, literal: Literal):
        match literal:
            case IntLiteral():
                self._compile_int(literal)
            case _:
                raise NotImplemented

    def _compile_int(self, literal: IntLiteral):
        integer: IntObject = IntObject(literal.value)
        self._emit(Opcode.CONSTANT, [self._add_constant(integer)])

    def _add_constant(self, constant: Object) -> int:
        self.constants.append(constant)
        return len(self.constants) - 1
        
    def _add_instruction(self, instruction: Instruction) -> int:
        self.instructions.append(instruction)
        return len(self.instructions) - 1

    def _emit(self, op: Opcode, operands: List[int]=[]) -> int:
        ins: Instruction = make(op, operands)
        pos: int = self._add_instruction(ins)
        return pos

