from typing import List, Tuple
from pycompiler.lexer import TokenType
from pycompiler.objects import (
    Object,
    IntObject
)
from pycompiler.code import Instructions, Opcode, make
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
    IntLiteral,
    BooleanLiteral,
)

Bytecode = Tuple[Instructions, List[Object]]
Error = str

class Compiler:
    def __init__(self):
        self.instructions: Instructions = Instructions()
        self.constants: List[Object] = []

    def compile(self, ast: List[Statement]) -> Error:
        for statement in ast:
            match statement:
                case ExpressionStatement():
                    err = self._compile_expression(statement.expr)
                    if err:
                        return err
                    # Need to cleanup the expression from the stack once its executed
                    self._emit(Opcode.POP, [])
                case _:
                    return f"{statement} type not implemented."

        return None

    def bytecode(self) -> Bytecode:
        return self.instructions, self.constants

    def _compile_expression(self, expression: Expression) -> Error:
        match expression:
            case LiteralExpression():
                err = self._compile_literal(expression.literal)
                if err:
                    return err
            case PrefixExpression():
                err = self._compile_expression(expression.right)
                if err:
                    return err

                match expression.operator.token_type:
                    case TokenType.MINUS:
                        self._emit(Opcode.MINUS, [])
                    case TokenType.BANG:
                        self._emit(Opcode.BANG, [])
                    case _:
                        return f"Prefix for {expression.operator.token_type} not implemented."
            case InfixExpression():
                # Swap order of operands for <
                if expression.operator.token_type == TokenType.LT:
                    err = self._compile_expression(expression.right)
                    if err:
                        return err
                    err = self._compile_expression(expression.left)
                    if err:
                        return err
                    self._emit(Opcode.GREATERTHAN, [])
                    return None

                err = self._compile_expression(expression.left)
                if err:
                    return err
                err = self._compile_expression(expression.right)
                if err:
                    return err

                match expression.operator.token_type:
                    case TokenType.PLUS:
                        self._emit(Opcode.ADD, [])
                    case TokenType.MINUS:
                        self._emit(Opcode.SUB, [])
                    case TokenType.ASTERISK:
                        self._emit(Opcode.MUL, [])
                    case TokenType.SLASH:
                        self._emit(Opcode.DIV, [])
                    case TokenType.EQ:
                        self._emit(Opcode.EQUAL, [])
                    case TokenType.NOT_EQ:
                        self._emit(Opcode.NOTEQUAL, [])
                    case TokenType.GT:
                        self._emit(Opcode.GREATERTHAN, [])
                    case _:
                        return f"Infix for {expression.operator.token_type} not implemented."
            case _:
                return f"Expression {expression} not implemented"

    def _compile_literal(self, literal: Literal):
        match literal:
            case IntLiteral():
                err = self._compile_int(literal)
                if err:
                    return err
            case BooleanLiteral():
                err = self._compile_boolean(literal)
                if err:
                    return err
            case _:
                return f"Literal {literal} not implemented"

    def _compile_int(self, literal: IntLiteral):
        integer: IntObject = IntObject(literal.value)
        self._emit(Opcode.CONSTANT, [self._add_constant(integer)])

    def _compile_boolean(self, literal: BooleanLiteral):
        if literal.value:
            self._emit(Opcode.TRUE, [])
        else:
            self._emit(Opcode.FALSE, [])

    def _add_constant(self, constant: Object) -> int:
        self.constants.append(constant)
        return len(self.constants) - 1
        
    def _add_instruction(self, instruction: Instructions) -> int:
        pos: int = len(self.instructions)
        self.instructions += instruction
        return pos

    def _emit(self, op: Opcode, operands: List[int]=[]) -> int:
        ins: Instructions = make(op, operands)
        pos: int = self._add_instruction(ins)
        return pos

