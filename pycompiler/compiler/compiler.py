from typing import List, Tuple
from pycompiler.lexer import TokenType
from pycompiler.objects import Object, IntObject, StringObject
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
    IfExpression,
    Literal,
    IntLiteral,
    BooleanLiteral,
    StringLiteral,
    ArrayLiteral,
    MapLiteral,
    IdentifierLiteral,
)

from .symbols import SymbolTable, Symbol

Bytecode = Tuple[Instructions, List[Object]]
Error = str


class EmittedInstruction:
    def __init__(self, opcode: Opcode, pos: int):
        self.opcode = opcode
        self.pos = pos


class Compiler:
    def __init__(self):
        self.instructions: Instructions = Instructions()
        self.constants: List[Object] = []

        self.last_ins = EmittedInstruction(Opcode.NULL, 9999)
        self.prev_ins = EmittedInstruction(Opcode.NULL, 9999)

        self.symbol_table: SymbolTable = SymbolTable()

    def compile(self, ast: List[Statement]) -> Error:
        for statement in ast:
            match statement:
                case ExpressionStatement():
                    err = self._compile_expression(statement.expr)
                    if err:
                        return err
                    # Need to cleanup the expression from the stack once its executed
                    self._emit(Opcode.POP, [])
                case LetStatement():
                    err = self._compile_expression(statement.expr)
                    if err:
                        return err

                    # Assign result of expression to identifier
                    symbol = self.symbol_table.define(statement.ident.token_value)
                    self._emit(Opcode.SETGLOBAL, [symbol.index])
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
                    case TokenType.LBRACKET:
                        self._emit(Opcode.INDEX, [])
                    case _:
                        return f"Infix for {expression.operator.token_type} not implemented."
            case IfExpression():
                err = self._compile_expression(expression.condition)
                if err:
                    return err
                jumpcond_op_pos: int = self._emit(Opcode.JUMPCOND, [9999])
                err = self.compile(expression.consequence.statements)
                if err:
                    return err
                if self._last_ins_is_pop():
                    self._remove_last_ins()
                jump_op_pos: int = self._emit(Opcode.JUMP, [9999])
                after_cons_pos = len(self.instructions)
                self._change_operand(jumpcond_op_pos, [after_cons_pos])

                if expression.alternative:
                    err = self.compile(expression.alternative.statements)
                    if err:
                        return err
                    if self._last_ins_is_pop():
                        self._remove_last_ins()
                else:
                    self._emit(Opcode.NULL, [])
                after_alt_pos = len(self.instructions)
                self._change_operand(jump_op_pos, [after_alt_pos])

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
            case StringLiteral():
                err = self._compile_string(literal)
                if err:
                    return err
            case ArrayLiteral():
                err = self._compile_array(literal)
                if err:
                    return err
            case MapLiteral():
                err = self._compile_map(literal)
                if err:
                    return err
            case IdentifierLiteral():
                result, symbol = self.symbol_table.resolve(literal.token.token_value)
                if not result:
                    return f"Cannot resolve identifier {literal.token.token_value}"
                self._emit(Opcode.GETGLOBAL, [symbol.index])
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

    def _compile_string(self, literal: StringLiteral):
        string_obj: StringObject = StringObject(literal.value)
        self._emit(Opcode.CONSTANT, [self._add_constant(string_obj)])

    def _compile_array(self, literal: ArrayLiteral):
        for member in literal.members:
            err = self._compile_expression(member)
            if err:
                return err
        self._emit(Opcode.ARRAY, [len(literal.members)])

    def _compile_map(self, literal: MapLiteral):
        for pair in literal.pairs:
            err = self._compile_expression(pair[0])
            if err:
                return err
            err = self._compile_expression(pair[1])
            if err:
                return err
        self._emit(Opcode.MAP, [len(literal.pairs)])

    def _add_constant(self, constant: Object) -> int:
        self.constants.append(constant)
        return len(self.constants) - 1

    def _add_instruction(self, instruction: Instructions) -> int:
        pos: int = len(self.instructions)
        self.instructions += instruction
        return pos

    def _emit(self, op: Opcode, operands: List[int] = []) -> int:
        ins: Instructions = make(op, operands)
        pos: int = self._add_instruction(ins)
        self.prev_ins = self.last_ins
        self.last_ins = EmittedInstruction(op, pos)
        return pos

    def _last_ins_is_pop(self) -> bool:
        return self.last_ins.opcode == Opcode.POP

    def _remove_last_ins(self) -> None:
        self.instructions = self.instructions[: self.last_ins.pos]
        self.last_ins = self.prev_ins

    def _replace_ins(self, pos: int, new_ins: Instructions) -> None:
        self.instructions[pos : pos + len(new_ins)] = new_ins

    def _change_operand(self, op_pos: int, operands: List[int]) -> None:
        new_ins = make(Opcode(self.instructions[op_pos]), operands)
        self._replace_ins(op_pos, new_ins)
