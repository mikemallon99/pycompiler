from pycompiler.lexer import Lexer, Token, TokenType
from pycompiler.parser import (
    Parser, 
    Statement,
    IdentifierLiteral, 
    IntLiteral, 
    StringLiteral, 
    FunctionLiteral, 
    BooleanLiteral,
    ArrayLiteral,
    Expression,
    LiteralExpression,
    LetStatement,
    ReturnStatement,
    ExpressionStatement,
    BlockStatement,
)

from typing import List


def assert_parser_output(test_program: str, expected_ast: List[Statement]):
    program = Parser(Lexer(test_program)).parse()
    assert program == expected_ast

def test_identifier_literal():
    assert_parser_output(
        "test_identifier", 
        [
            ExpressionStatement(
                LiteralExpression(
                    IdentifierLiteral(
                        Token(TokenType.IDENT, "test_identifier")
                    )
                )
            )
        ]
    )

def test_int_literal():
    assert_parser_output(
        "69", 
        [
            ExpressionStatement(
                LiteralExpression(
                    IntLiteral(
                        Token(TokenType.INT, "69"),
                        69
                    )
                )
            )
        ]
    )

def test_string_literal():
    assert_parser_output(
        "\"test string\"", 
        [
            ExpressionStatement(
                LiteralExpression(
                    StringLiteral(
                        Token(TokenType.STRING, "test string"),
                        "test string"
                    )
                )
            )
        ]
    )

def test_function_literal():
    assert_parser_output(
        "fn (x, y) { return x }", 
        [
            ExpressionStatement(
                LiteralExpression(
                    FunctionLiteral(
                        [
                            Token(TokenType.IDENT, "x"),
                            Token(TokenType.IDENT, "y")
                        ],
                        BlockStatement(
                            [
                                ReturnStatement(
                                    LiteralExpression(
                                        IdentifierLiteral(
                                            Token(TokenType.IDENT, "x")
                                        )
                                    )
                                ),
                            ]
                        )
                    )
                )
            )
        ]
    )

def test_boolean_literal():
    assert_parser_output(
        "true", 
        [
            ExpressionStatement(
                LiteralExpression(
                    BooleanLiteral(
                        Token(TokenType.TRUE, "true"),
                        True
                    )
                )
            )
        ]
    )
    assert_parser_output(
        "false", 
        [
            ExpressionStatement(
                LiteralExpression(
                    BooleanLiteral(
                        Token(TokenType.FALSE, "false"),
                        False
                    )
                )
            )
        ]
    )

def test_array_literal():
    assert_parser_output(
        "[1, 2, 3]", 
        [
            ExpressionStatement(
                LiteralExpression(
                    ArrayLiteral(
                        [
                            LiteralExpression(IntLiteral(Token(TokenType.INT, "1"), 1)),
                            LiteralExpression(IntLiteral(Token(TokenType.INT, "2"), 2)),
                            LiteralExpression(IntLiteral(Token(TokenType.INT, "3"), 3))
                        ]
                    )
                )
            )
        ]
    )

