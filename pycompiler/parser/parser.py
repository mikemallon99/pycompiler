from pycompiler.lexer import TokenType, Token
from typing import Optional
from enum import Enum


class Precedence(Enum):
    LOWEST = 1
    PREFIX = 10


def get_precedence(token_type: TokenType) -> Precedence:
    return Precedence.LOWEST


class Literal:
    pass


class IdentifierLiteral(Literal):
    def __init__(self, token: Token):
        self.token: Token = token


class IntLiteral(Literal):
    def __init__(self, token: Token, value: int):
        self.token: Token = token
        self.value: int = value


class StringLiteral(Literal):
    def __init__(self, token: Token, value: str):
        self.token: Token = token
        self.value: str = value


class FunctionLiteral(Literal):
    def __init__(self, arguments: List[Token], body: BlockStatement):
        self.arguments: List[Token] = arguments
        self.body: BlockStatement = body


class BooleanLiteral(Literal):
    def __init__(self, token: Token, value: bool):
        self.token: Token = token
        self.value: bool = value


class ArrayLiteral(Literal):
    def __init__(self, members: List[Expression]):
        self.members: List[Expression] = members


ExpressionPair = Tuple[Expression, Expression]
class MapLiteral(Literal):
    def __init__(self, pairs: List[ExpressionPair]):
        self.pairs: List[ExpressionPair] = pairs


class Expression:
    pass


class LiteralExpression(Expression):
    def __init__(self, literal: Literal):
        self.literal: Literal = literal


class PrefixExpression(Expression):
    def __init__(self, operator: Token, right: Expression):
        self.operator: Token = operator
        self.right: Expression = right


class InfixExpression(Expression):
    def __init__(self, left: Expression, operator: Token, right: Expression):
        self.left: Expression = left
        self.operator: Token = operator
        self.right: Expression = right


class IfExpression(Expression):
    def __init__(self, condition: Expression, consequence: BlockStatement, alternative: Optional[BlockStatement] = None):
        self.condition: Expression = condition
        self.consequence: BlockStatement = consequence
        self.alternative: Optional[BlockStatement] = alternative


class CallExpression(Expression):
    def __init__(self, func: Expression, args: List[Expression]):
        self.func: Expression = func
        self.args: List[Expression] = args


class Statement:
    pass


class LetStatement(Statement):
    def __init__(self, ident: Token, expr: Expression):
        assert ident.token_type == TokenType.IDENT
        self.ident: Token = ident
        self.expr: Expression = expr


class ReturnStatement(Statement):
    def __init__(self, expr: Expression):
        self.expr: Expression = expr


class ExpressionStatement(Statement):
    def __init__(self, expr: Expression):
        self.expr: Expression = expr


class BlockStatement(Statement):
    def __init__(self, statements: List[Statement]):
        self.statements: List[Statement] = statements


class UnexpectedTokenError(Exception):
    def __init__(self, token_type: TokenType, expected_type: TokenType):
        super().__init__(f"Expected: {expected_type.value}, Got: {token_type.value}")


class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer: Lexer = lexer
        self.cur_token: Token = self.lexer.next_token()
        self.peek_token: Token = self.lexer.next_token()
        self.errors: List[str] = []

    def parse(self) -> List[Statement]:
        program: List[Statement] = []

        while self.cur_token.token_type != TokenType.EOF:
            program.append(self._parse_statement())
            self._next_token()

        return program

    def _parse_statement(self) -> Statement:
        match self.cur_token.token_type:
            case TokenType.LET:
                self._parse_let_statement()
            case TokenType.RETURN:
                self._parse_return_statement()
            case _:
                self._parse_expression_statement()

        # Semicolons optional
        if self.peek_token.token_type == TokenType.SEMICOLON:
            self._next_token()

    def _parse_let_statement(self) -> LetStatement:
        # Skip over let token
        identifier: Token = self._expect_peek(TokenType.IDENT)
        self._expect_peek(TokenType.ASSIGN)
        return LetStatement(identifier, self._parse_expression())

    def _parse_return_statement(self) -> ReturnStatement:
        # Skip over return token
        self._next_token()
        return ReturnStatement(self._parse_expression())

    def _parse_expression_statement(self) -> ExpressionStatement:
        return ExpressionStatement(self._parse_expression())

    def _parse_block_statement(self) -> BlockStatement:
        statements: List[Statement] = []
        while self.cur_token.token_type != TokenType.RBRACE:
            statements.append(self._parse_statement())
            self._next_token()
        return BlockStatement(statements)

    def _parse_expression(self, precedence: Precedence):
        if self.cur_token.token_type in [TokenType.IDENT, TokenType.INT, TokenType.TRUE, TokenType.FALSE, TokenType.STRING]:
            left_expr = self._parse_literal()
        elif self.cur_token.token_type in [TokenType.MINUS, TokenType.BANG]:
            left_expr = self._parse_prefix()
        elif self.cur_token.token_type == TokenType.LPAREN:
            left_expr = self._parse_group()
        elif self.cur_token.token_type == TokenType.IF:
            left_expr = self._parse_if()
        elif self.cur_token.token_type == TokenType.FUNCTION:
            left_expr = self._parse_function()
        elif self.cur_token.token_type == TokenType.LBRACKET:
            left_expr = self._parse_array()
        elif self.cur_token.token_type == TokenType.LBRACE:
            left_expr = self._parse_map()
        else:
            raise Exception(f"Did not find expression function for token type {self.cur_token.token_type.value}")

        while self.peek_token.token_type != TokenType.SEMICOLON and precedence < self._get_precedence(self.peek_token):
            cur_token: Token = self._next_token()
            if cur_token.token_type == TokenType.LPAREN:
                left_expr = self._parse_call(left_expr)
            else:
                left_expr = self._parse_infix(left_expr)

        return left_expr

    def _parse_literal(self) -> LiteralExpression:
        match self.cur_token.token_type:
            case TokenType.IDENT:
                literal = IdentifierLiteral(self.cur_token)
            case TokenType.INT:
                literal = IntLiteral(self.cur_token, int(self.cur_token.token_value))
            case TokenType.TRUE:
                literal = BooleanLiteral(self.cur_token, True)
            case TokenType.FALSE:
                literal = BooleanLiteral(self.cur_token, False)
            case TokenType.STRING:
                literal = StringLiteral(self.cur_token, self.cur_token.token_value)
            case _:
                raise Exception(f"Cannot create literal expression from token type: {self.cur_token.token_type.value}")
        
        return LiteralExpression(literal)

    def _parse_prefix(self) -> PrefixExpression:
        operator: Token = self.cur_token
        self._next_token()
        return PrefixExpression(operator, self._parse_expression(Precedence.PREFIX))

    def _parse_group(self) -> Expression:
        # Skip over LPAREN token
        self._next_token()
        expression: Expression = self._parse_expression(Precedence.LOWEST)
        # Skip over RPAREN token
        self._expect_peek(TokenType.RPAREN)
        return expression

    def _parse_if(self) -> IfExpression:
        self._expect_peek(TokenType.LPAREN)
        self._next_token()
        condition: Expression = self._parse_expression(Precedence.LOWEST)
        self._expect_peek(TokenType.RPAREN)

        self._expect_peek(TokenType.LBRACE)
        self._next_token()
        consequence: BlockStatement = self._parse_block_statement(Precedence.LOWEST)

        if self.peek_token.token_type == TokenType.ELSE:
            self._next_token()
            self._expect_peek(TokenType.LBRACE)
            self._next_token()
            alternative: BlockStatement = self._parse_block_statement(Precedence.LOWEST)
            return IfExpression(condition, consequence, alternative)
        else:
            return IfExpression(condition, consequence)

    def _parse_function(self) -> FunctionLiteral:
        # Skip over fn keyword
        # Args list
        self._expect_peek(TokenType.LPAREN)
        fn_args: List[Token] = self._parse_function_params()

        # Function body
        self._expect_peek(TokenType.LBRACE)
        self._next_token()
        return FunctionLiteral(fn_args, self._parse_block_statement())

    def _parse_function_params(self) -> List[Token]:
        if self.peek_token.token_type == TokenType.RPAREN:
            self._next_token()
            return []

        params: List[Token] = []
        while True:
            params.append(self._next_token())
            if self._peek_token.token_type == TokenType.RPAREN:
                self._next_token()
                break
            else:
                self._expect_peek(TokenType.COMMA)

        return params

    def _parse_array(self) -> ArrayLiteral:
        self._next_token()
        if self.cur_token.token_type == TokenType.RBRACKET:
            return ArrayLiteral([])

        members: List[Expression] = []
        while True:
            members.append(self._parse_expression(Precedence.LOWEST))
            if self._peek_token.token_type == TokenType.RBRACKET:
                self._next_token()
                break
            else:
                self._expect_peek(TokenType.COMMA)
                self._next_token()

        return ArrayLiteral(members)

    def _parse_map(self) -> MapLiteral:
        self._next_token()
        if self.cur_token.token_type == TokenType.RBRACE:
            return MapLiteral([])

        pairs: List[ExpressionPair] = []
        while True:
            key_expression = self._parse_expression(Precedence.LOWEST)
            self._expect_token(TokenType.COLON)
            self._next_token()
            value_expression = self._parse_expression(Precedence.LOWEST)
            pairs.append((key_expression, value_expression))

            if self._peek_token.token_type == TokenType.RBRACE:
                self._next_token()
                break
            else:
                self._expect_peek(TokenType.COMMA)
                self._next_token()

        return MapLiteral(pairs)

    def _parse_call(self, function: Expression) -> CallExpression:
        # Parse arguments
        self._next_token()
        if self.cur_token.token_type == TokenType.RPAREN:
            return CallExpression(function, arguments)

        arguments: List[Expression] = []
        while True:
            arguments.append(self._parse_expression(Precedence.LOWEST))
            if self._peek_token.token_type == TokenType.RPAREN:
                self._next_token()
                break
            else:
                self._expect_peek(TokenType.COMMA)
                self._next_token()

        return CallExpression(function, arguments)
        

    def _parse_infix(self, left: Expression):
        operator: Token = self.cur_token
        self._next_token()
        # Parse expression in brackets for arrays
        if operator.token_type == TokenType.LBRACKET:
            return InfixExpression(left, operator, self._parse_expression(Precedence.LOWEST))
        # Regular infix expression
        else:
            return InfixExpression(left, operator, self._parse_expression(get_precedence(operator)))

    def _next_token(self) -> Token:
        self.cur_token = self.peek_token
        self.peek_token = self.lexer.next_token()
        return self.cur_token

    def _expect_peek(self, expect_type: TokenType) -> Token:
        if self.peek_token.token_type == expect_type:
            self._next_token()
            return self.cur_token
        else:
            raise UnexpectedTokenError(self.peek_token.token_type, expect_type)

