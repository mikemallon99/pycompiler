from pycompiler.lexer import TokenType, Token, Lexer
from typing import Optional, List, Tuple
from enum import IntEnum


class Precedence(IntEnum):
    LOWEST = 1
    EQUALS = 2
    LESSGREATER = 3
    SUM = 4
    PRODUCT = 5
    PREFIX = 6
    CALL = 7
    INDEX = 8


def get_precedence(token: Token) -> Precedence:
    match token.token_type:
        case TokenType.EQ:
            return Precedence.EQUALS
        case TokenType.NOT_EQ:
            return Precedence.EQUALS
        case TokenType.LT:
            return Precedence.LESSGREATER
        case TokenType.GT:
            return Precedence.LESSGREATER
        case TokenType.PLUS:
            return Precedence.SUM
        case TokenType.MINUS:
            return Precedence.SUM
        case TokenType.SLASH:
            return Precedence.PRODUCT
        case TokenType.ASTERISK:
            return Precedence.PRODUCT
        case TokenType.LPAREN:
            return Precedence.CALL
        case TokenType.LBRACKET:
            return Precedence.INDEX
        case _:
            return Precedence.LOWEST


class Statement:
    pass


class Expression:
    pass


class LetStatement(Statement):
    def __init__(self, ident: Token, expr: Expression):
        assert ident.token_type == TokenType.IDENT
        self.ident: Token = ident
        self.expr: Expression = expr

    def __eq__(self, other: object):
        if not isinstance(other, LetStatement):
            return NotImplemented
        return self.ident == other.ident and self.expr == other.expr

    def __repr__(self):
        return f"<LetStatement: ident={self.ident}, expr={self.expr}>"


class ReturnStatement(Statement):
    def __init__(self, expr: Expression):
        self.expr: Expression = expr

    def __eq__(self, other: object):
        if not isinstance(other, ReturnStatement):
            return NotImplemented
        return self.expr == other.expr

    def __repr__(self):
        return f"<ReturnStatement: expr={self.expr}>"


class ExpressionStatement(Statement):
    def __init__(self, expr: Expression):
        self.expr: Expression = expr

    def __eq__(self, other: object):
        if not isinstance(other, ExpressionStatement):
            return NotImplemented
        return self.expr == other.expr

    def __repr__(self):
        return f"<ExpressionStatement: expr={self.expr}>"


class BlockStatement(Statement):
    def __init__(self, statements: List[Statement]):
        self.statements: List[Statement] = statements

    def __eq__(self, other: object):
        if not isinstance(other, BlockStatement):
            return NotImplemented
        return self.statements == other.statements

    def __repr__(self):
        return f"<BlockStatement: statements={self.statements}>"


class Literal:
    pass


class IdentifierLiteral(Literal):
    def __init__(self, token: Token):
        self.token: Token = token

    def __eq__(self, other: object):
        if not isinstance(other, IdentifierLiteral):
            return NotImplemented
        return self.token == other.token

    def __repr__(self):
        return f"<IdentifierLiteral: token={self.token}>"


class IntLiteral(Literal):
    def __init__(self, token: Token, value: int):
        self.token: Token = token
        self.value: int = value

    def __eq__(self, other: object):
        if not isinstance(other, IntLiteral):
            return NotImplemented
        return self.token == other.token and self.value == other.value

    def __repr__(self):
        return f"<IntLiteral: token={self.token}, value={self.value}>"


class StringLiteral(Literal):
    def __init__(self, token: Token, value: str):
        self.token: Token = token
        self.value: str = value

    def __eq__(self, other: object):
        if not isinstance(other, StringLiteral):
            return NotImplemented
        return self.token == other.token and self.value == other.value

    def __repr__(self):
        return f"<StringLiteral: token={self.token}, value={self.value}>"


class FunctionLiteral(Literal):
    def __init__(self, arguments: List[Token], body: BlockStatement):
        self.arguments: List[Token] = arguments
        self.body: BlockStatement = body

    def __eq__(self, other: object):
        if not isinstance(other, FunctionLiteral):
            return NotImplemented
        return self.arguments == other.arguments and self.body == other.body

    def __repr__(self):
        return f"<FunctionLiteral: arguments={self.arguments}, body={self.body}>"


class BooleanLiteral(Literal):
    def __init__(self, token: Token, value: bool):
        self.token: Token = token
        self.value: bool = value

    def __eq__(self, other: object):
        if not isinstance(other, BooleanLiteral):
            return NotImplemented
        return self.token == other.token and self.value == other.value

    def __repr__(self):
        return f"<BooleanLiteral: token={self.token}, value={self.value}>"


class ArrayLiteral(Literal):
    def __init__(self, members: List[Expression]):
        self.members: List[Expression] = members

    def __eq__(self, other: object):
        if not isinstance(other, ArrayLiteral):
            return NotImplemented
        return self.members == other.members

    def __repr__(self):
        return f"<ArrayLiteral: members={self.members}>"


ExpressionPair = Tuple[Expression, Expression]


class MapLiteral(Literal):
    def __init__(self, pairs: List[ExpressionPair]):
        self.pairs: List[ExpressionPair] = pairs

    def __eq__(self, other: object):
        if not isinstance(other, MapLiteral):
            return NotImplemented
        return self.pairs == other.pairs

    def __repr__(self):
        return f"<MapLiteral: pairs={self.pairs}>"


class LiteralExpression(Expression):
    def __init__(self, literal: Literal):
        self.literal: Literal = literal

    def __eq__(self, other: object):
        if not isinstance(other, LiteralExpression):
            return NotImplemented
        return self.literal == other.literal

    def __repr__(self):
        return f"<LiteralExpression: literal={self.literal}>"


class PrefixExpression(Expression):
    def __init__(self, operator: Token, right: Expression):
        self.operator: Token = operator
        self.right: Expression = right

    def __eq__(self, other: object):
        if not isinstance(other, PrefixExpression):
            return NotImplemented
        return self.operator == other.operator and self.right == other.right

    def __repr__(self):
        return f"<PrefixExpression: operator={self.operator}, right={self.right}>"


class InfixExpression(Expression):
    def __init__(self, left: Expression, operator: Token, right: Expression):
        self.left: Expression = left
        self.operator: Token = operator
        self.right: Expression = right

    def __eq__(self, other: object):
        if not isinstance(other, InfixExpression):
            return NotImplemented
        return (
            self.left == other.left
            and self.operator == other.operator
            and self.right == other.right
        )

    def __repr__(self):
        return f"<InfixExpression: left={self.left}, operator={self.operator}, right={self.right}>"


class IfExpression(Expression):
    def __init__(
        self,
        condition: Expression,
        consequence: BlockStatement,
        alternative: Optional[BlockStatement] = None,
    ):
        self.condition: Expression = condition
        self.consequence: BlockStatement = consequence
        self.alternative: Optional[BlockStatement] = alternative

    def __eq__(self, other: object):
        if not isinstance(other, IfExpression):
            return NotImplemented
        return (
            self.condition == other.condition
            and self.consequence == other.consequence
            and self.alternative == other.alternative
        )

    def __repr__(self):
        return f"<IfExpression: condition={self.condition}, consequence={self.consequence}, alternative={self.alternative}>"


class CallExpression(Expression):
    def __init__(self, func: Expression, args: List[Expression]):
        self.func: Expression = func
        self.args: List[Expression] = args

    def __eq__(self, other: object):
        if not isinstance(other, CallExpression):
            return NotImplemented
        return self.func == other.func and self.args == other.args

    def __repr__(self):
        return f"<CallExpression: func={self.func}, args={self.args}>"


class UnexpectedTokenError(Exception):
    def __init__(self, token_type: TokenType, expected_type: TokenType):
        super().__init__(f"Expected: {expected_type.value}, Got: {token_type.value}")


class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer: Lexer = lexer
        self.cur_token: Token = self.lexer.next_token()
        self.peek_token: Token = self.lexer.next_token()

    def parse(self) -> List[Statement]:
        program: List[Statement] = []

        while self.cur_token.token_type != TokenType.EOF:
            program.append(self._parse_statement())
            self._next_token()

        return program

    def _parse_statement(self) -> Statement:
        statement: Statement
        match self.cur_token.token_type:
            case TokenType.LET:
                statement = self._parse_let_statement()
            case TokenType.RETURN:
                statement = self._parse_return_statement()
            case _:
                statement = self._parse_expression_statement()

        # Semicolons optional
        if self.peek_token.token_type == TokenType.SEMICOLON:
            self._next_token()

        return statement

    def _parse_let_statement(self) -> LetStatement:
        # Skip over let token
        identifier: Token = self._expect_peek(TokenType.IDENT)
        self._expect_peek(TokenType.ASSIGN)
        self._next_token()
        return LetStatement(identifier, self._parse_expression(Precedence.LOWEST))

    def _parse_return_statement(self) -> ReturnStatement:
        # Skip over return token
        self._next_token()
        return ReturnStatement(self._parse_expression(Precedence.LOWEST))

    def _parse_expression_statement(self) -> ExpressionStatement:
        return ExpressionStatement(self._parse_expression(Precedence.LOWEST))

    def _parse_block_statement(self) -> BlockStatement:
        statements: List[Statement] = []
        while self.cur_token.token_type != TokenType.RBRACE:
            statements.append(self._parse_statement())
            self._next_token()
        return BlockStatement(statements)

    def _parse_expression(self, precedence: Precedence) -> Expression:
        left_expr: Expression
        if self.cur_token.token_type in [
            TokenType.IDENT,
            TokenType.INT,
            TokenType.TRUE,
            TokenType.FALSE,
            TokenType.STRING,
            TokenType.FUNCTION,
            TokenType.LBRACKET,
            TokenType.LBRACE,
        ]:
            left_expr = self._parse_literal()
        elif self.cur_token.token_type in [TokenType.MINUS, TokenType.BANG]:
            left_expr = self._parse_prefix()
        elif self.cur_token.token_type == TokenType.LPAREN:
            left_expr = self._parse_group()
        elif self.cur_token.token_type == TokenType.IF:
            left_expr = self._parse_if()
        else:
            raise Exception(
                f"Did not find expression function for token type {self.cur_token.token_type.value}"
            )

        while (
            self.peek_token.token_type != TokenType.SEMICOLON
            and precedence < get_precedence(self.peek_token)
        ):
            cur_token: Token = self._next_token()
            if cur_token.token_type == TokenType.LPAREN:
                left_expr = self._parse_call(left_expr)
            else:
                left_expr = self._parse_infix(left_expr)

        return left_expr

    def _parse_literal(self) -> LiteralExpression:
        literal: Literal
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
            case TokenType.FUNCTION:
                literal = self._parse_function()
            case TokenType.LBRACKET:
                literal = self._parse_array()
            case TokenType.LBRACE:
                literal = self._parse_map()
            case _:
                raise Exception(
                    f"Cannot create literal expression from token type: {self.cur_token.token_type.value}"
                )

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
        consequence: BlockStatement = self._parse_block_statement()

        if self.peek_token.token_type == TokenType.ELSE:
            self._next_token()
            self._expect_peek(TokenType.LBRACE)
            self._next_token()
            alternative: BlockStatement = self._parse_block_statement()
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
            if self.peek_token.token_type == TokenType.RPAREN:
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
            if self.peek_token.token_type == TokenType.RBRACKET:
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
            self._expect_peek(TokenType.COLON)
            self._next_token()
            value_expression = self._parse_expression(Precedence.LOWEST)
            pairs.append((key_expression, value_expression))

            if self.peek_token.token_type == TokenType.RBRACE:
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
            return CallExpression(function, [])

        arguments: List[Expression] = []
        while True:
            arguments.append(self._parse_expression(Precedence.LOWEST))
            if self.peek_token.token_type == TokenType.RPAREN:
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
            expression = InfixExpression(
                left, operator, self._parse_expression(Precedence.LOWEST)
            )
            self._expect_peek(TokenType.RBRACKET)
            return expression
        # Regular infix expression
        else:
            return InfixExpression(
                left, operator, self._parse_expression(get_precedence(operator))
            )

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
