from typing import List, Tuple
from pycompiler.lexer import TokenType
from pycompiler.objects import Object, IntObject, StringObject, CompiledFunctionObject, BUILTINS
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
    CallExpression,
    Literal,
    IntLiteral,
    FunctionLiteral,
    BooleanLiteral,
    StringLiteral,
    ArrayLiteral,
    MapLiteral,
    IdentifierLiteral,
)

from .symbols import SymbolTable, GLOBALSCOPE, LOCALSCOPE, BUILTINSCOPE, FREESCOPE, FUNCTIONSCOPE


Bytecode = Tuple[Instructions, List[Object]]
Error = str


class EmittedInstruction:
    def __init__(self, opcode: Opcode, pos: int):
        self.opcode = opcode
        self.pos = pos


class CompilerScope():
    def __init__(self) -> None:
        self.instructions: Instructions = Instructions()
        self.last_ins = EmittedInstruction(Opcode.NULL, 9999)
        self.prev_ins = EmittedInstruction(Opcode.NULL, 9999)


class Compiler:
    def __init__(self) -> None:
        self.constants: List[Object] = []

        self.symbol_table: SymbolTable = SymbolTable()
        for i, builtin in enumerate(BUILTINS):
            self.symbol_table.define_builtin(i, builtin.name)

        self.scopes: List[CompilerScope] = [CompilerScope()]
        self.scope_index: int = 0

    def compile(self, ast: List[Statement]) -> Error | None:
        for statement in ast:
            match statement:
                case ExpressionStatement():
                    err = self._compile_expression(statement.expr)
                    if err:
                        return err
                    # Need to cleanup the expression from the stack once its executed
                    self._emit(Opcode.POP, [])
                case LetStatement():
                    symbol = self.symbol_table.define(statement.ident.token_value)
                    err = self._compile_expression(statement.expr)
                    if err:
                        return err

                    # Assign result of expression to identifier
                    if symbol.scope == GLOBALSCOPE:
                        self._emit(Opcode.SETGLOBAL, [symbol.index])
                    else:
                        self._emit(Opcode.SETLOCAL, [symbol.index])
                case ReturnStatement():
                    err = self._compile_expression(statement.expr)
                    if err:
                        return err
                    self._emit(Opcode.RETURNVALUE, [])
                case _:
                    return f"{statement} type not implemented."

        return None

    def bytecode(self) -> Bytecode:
        return self._current_instructions(), self.constants

    def _compile_expression(self, expression: Expression) -> Error | None:
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
                if self._last_ins_is(Opcode.POP):
                    self._remove_last_ins()
                jump_op_pos: int = self._emit(Opcode.JUMP, [9999])
                after_cons_pos = len(self._current_instructions())
                self._change_operand(jumpcond_op_pos, [after_cons_pos])

                if expression.alternative:
                    err = self.compile(expression.alternative.statements)
                    if err:
                        return err
                    if self._last_ins_is(Opcode.POP):
                        self._remove_last_ins()
                else:
                    self._emit(Opcode.NULL, [])
                after_alt_pos = len(self._current_instructions())
                self._change_operand(jump_op_pos, [after_alt_pos])
            case CallExpression():
                err = self._compile_expression(expression.func)
                if err:
                    return err
                for arg in expression.args:
                    err = self._compile_expression(arg) 
                    if err:
                        return err
                self._emit(Opcode.CALL, [len(expression.args)])
            case _:
                return f"Expression {expression} not implemented"

        return None

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
                if not result or not symbol:
                    return f"Cannot resolve identifier {literal.token.token_value}"
                err = self._load_symbol(symbol)
                if err:
                    return err
            case FunctionLiteral():
                self._enter_scope()
                for arg in literal.arguments:
                    symbol = self.symbol_table.define(arg.token_value)
                if literal.name:
                    self.symbol_table.define_function_name(literal.name)
                err = self.compile(literal.body.statements)
                if err:
                    return err
                if self._last_ins_is(Opcode.POP):
                    self._remove_last_ins()
                    self._emit(Opcode.RETURNVALUE, [])
                if not self._last_ins_is(Opcode.RETURNVALUE):
                    self._emit(Opcode.RETURN, [])
                free_symbols = self.symbol_table.free_symbols
                num_locals = self.symbol_table.num_defs
                instructions = self._leave_scope()

                for s in free_symbols:
                    self._load_symbol(s)

                self._emit(Opcode.CLOSURE, [self._add_constant(CompiledFunctionObject(instructions, num_locals, len(literal.arguments))), len(free_symbols)])
            case _:
                return f"Literal {literal} not implemented"

    def _load_symbol(self, symbol):
        if symbol.scope == GLOBALSCOPE:
            self._emit(Opcode.GETGLOBAL, [symbol.index])
        elif symbol.scope == BUILTINSCOPE:
            self._emit(Opcode.GETBUILTIN, [symbol.index])
        elif symbol.scope == FREESCOPE:
            self._emit(Opcode.GETFREE, [symbol.index])
        elif symbol.scope == FUNCTIONSCOPE:
            self._emit(Opcode.CURRENTCLOSURE, [])
        else:
            self._emit(Opcode.GETLOCAL, [symbol.index])

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
        pos: int = len(self._current_instructions())
        self._current_scope().instructions += instruction
        return pos

    def _emit(self, op: Opcode, operands: List[int] = []) -> int:
        ins: Instructions = make(op, operands)
        pos: int = self._add_instruction(ins)
        self._current_scope().prev_ins = self._current_scope().last_ins
        self._current_scope().last_ins = EmittedInstruction(op, pos)
        return pos

    def _enter_scope(self):
        self.scope_index += 1
        self.scopes.append(CompilerScope())
        self.symbol_table = SymbolTable(self.symbol_table)

    def _leave_scope(self) -> Instructions:
        self.scope_index -= 1
        scope = self.scopes.pop()
        self.symbol_table = self.symbol_table.outer
        return scope.instructions

    def _current_scope(self) -> CompilerScope:
        return self.scopes[self.scope_index]

    def _current_instructions(self) -> Instructions:
        return self._current_scope().instructions

    def _last_ins_is(self, opcode: Opcode) -> bool:
        return self._current_scope().last_ins.opcode == opcode

    def _remove_last_ins(self) -> None:
        self._current_scope().instructions = self._current_instructions()[: self._current_scope().last_ins.pos]
        self.last_ins = self._current_scope().prev_ins

    def _replace_ins(self, pos: int, new_ins: Instructions) -> None:
        self._current_scope().instructions[pos : pos + len(new_ins)] = new_ins

    def _change_operand(self, op_pos: int, operands: List[int]) -> None:
        new_ins = make(Opcode(self._current_instructions()[op_pos]), operands)
        self._replace_ins(op_pos, new_ins)
