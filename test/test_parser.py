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
    ExpressionPair,
    MapLiteral,
    Expression,
    LiteralExpression,
    PrefixExpression,
    InfixExpression,
    CallExpression,
    IfExpression,
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

def test_map_literal():
    assert_parser_output(
        "{\"one\": 1, 2: 2, function(): \"three\"}", 
        [
            ExpressionStatement(
                LiteralExpression(
                    MapLiteral(
                        [
                            (
                                LiteralExpression(StringLiteral(Token(TokenType.STRING, "one"), "one")),
                                LiteralExpression(IntLiteral(Token(TokenType.INT, "1"), 1))
                            ),
                            (
                                LiteralExpression(IntLiteral(Token(TokenType.INT, "2"), 2)),
                                LiteralExpression(IntLiteral(Token(TokenType.INT, "2"), 2))
                            ),
                            (
                                CallExpression(
                                    LiteralExpression(
                                        IdentifierLiteral(
                                            Token(TokenType.IDENT, "function"),
                                        )
                                    ),
                                    []
                                ),
                                LiteralExpression(StringLiteral(Token(TokenType.STRING, "three"), "three"))
                            ),
                        ]
                    )
                )
            )
        ]
    )

def test_let_statement():
    assert_parser_output(
        "let x = 21", 
        [
            LetStatement(
                Token(TokenType.IDENT, "x"),
                LiteralExpression(
                    IntLiteral(
                        Token(TokenType.INT, "21"),
                        21
                    )
                )
            )
        ]
    )

def test_return_statement():
    assert_parser_output(
        "return 21", 
        [
            ReturnStatement(
                LiteralExpression(
                    IntLiteral(
                        Token(TokenType.INT, "21"),
                        21
                    )
                )
            )
        ]
    )

def test_infix_expression():
    assert_parser_output(
        "12 * test", 
        [
            ExpressionStatement(
                InfixExpression(
                    LiteralExpression(
                        IntLiteral(
                            Token(TokenType.INT, "12"),
                            12
                        )
                    ),
                    Token(TokenType.ASTERISK),
                    LiteralExpression(
                        IdentifierLiteral(
                            Token(TokenType.IDENT, "test")
                        )
                    )
                )
            )
        ]
    )
    assert_parser_output(
        "test[0]", 
        [
            ExpressionStatement(
                InfixExpression(
                    LiteralExpression(
                        IdentifierLiteral(
                            Token(TokenType.IDENT, "test"),
                        )
                    ),
                    Token(TokenType.LBRACKET),
                    LiteralExpression(
                        IntLiteral(
                            Token(TokenType.INT, "0"),
                            0
                        )
                    )
                )
            )
        ]
    )

def test_prefix_expression():
    assert_parser_output(
        "-12", 
        [
            ExpressionStatement(
                PrefixExpression(
                    Token(TokenType.MINUS),
                    LiteralExpression(
                        IntLiteral(
                            Token(TokenType.INT, "12"),
                            12
                        )
                    )
                )
            )
        ]
    )
    assert_parser_output(
        "!12", 
        [
            ExpressionStatement(
                PrefixExpression(
                    Token(TokenType.BANG),
                    LiteralExpression(
                        IntLiteral(
                            Token(TokenType.INT, "12"),
                            12
                        )
                    )
                )
            )
        ]
    )

def test_if_expression():
    assert_parser_output(
        "if (true) { return x } else { return false }", 
        [
            ExpressionStatement(
                IfExpression(
                    LiteralExpression(
                        BooleanLiteral(
                            Token(TokenType.TRUE, "true"),
                            True
                        )
                    ),
                    BlockStatement(
                        [ReturnStatement(LiteralExpression(IdentifierLiteral(Token(TokenType.IDENT, "x"))))]
                    ),
                    BlockStatement(
                        [ReturnStatement(LiteralExpression(BooleanLiteral(Token(TokenType.FALSE, "false"), False)))]
                    ),
                )
            )
        ]
    )
    assert_parser_output(
        "if (true) { return x }", 
        [
            ExpressionStatement(
                IfExpression(
                    LiteralExpression(
                        BooleanLiteral(
                            Token(TokenType.TRUE, "true"),
                            True
                        )
                    ),
                    BlockStatement(
                        [ReturnStatement(LiteralExpression(IdentifierLiteral(Token(TokenType.IDENT, "x"))))]
                    ),
                )
            )
        ]
    )

def test_call_expression():
    assert_parser_output(
        "function(2, true)", 
        [
            ExpressionStatement(
                CallExpression(
                    LiteralExpression(
                        IdentifierLiteral(
                            Token(TokenType.IDENT, "function"),
                        )
                    ),
                    [
                        LiteralExpression(
                            IntLiteral(
                                Token(TokenType.INT, "2"),
                                2
                            )
                        ),
                        LiteralExpression(
                            BooleanLiteral(
                                Token(TokenType.TRUE, "true"),
                                True
                            )
                        ),
                    ]
                )
            )
        ]
    )

def test_multiple_statements():
    assert_parser_output(
        "let x = 69; 2 * 2; return x;", 
        [
            LetStatement(
                Token(TokenType.IDENT, "x"),
                LiteralExpression(
                    IntLiteral(
                        Token(TokenType.INT, "69"),
                        69
                    )
                )
            ),
            ExpressionStatement(
                InfixExpression(
                    LiteralExpression(
                        IntLiteral(
                            Token(TokenType.INT, "2"),
                            2
                        )
                    ),
                    Token(TokenType.ASTERISK),
                    LiteralExpression(
                        IntLiteral(
                            Token(TokenType.INT, "2"),
                            2
                        )
                    ),
                )
            ),
            ReturnStatement(
                LiteralExpression(
                    IdentifierLiteral(
                        Token(TokenType.IDENT, "x")
                    )
                )
            ),
        ]
    )

def test_precedence():
    assert_parser_output(
        "12 + x * ( y - 3 )", 
        [
            ExpressionStatement(
                InfixExpression(
                    LiteralExpression(
                        IntLiteral(
                            Token(TokenType.INT, "12"),
                            12
                        )
                    ),
                    Token(TokenType.PLUS),
                    InfixExpression(
                        LiteralExpression(
                            IdentifierLiteral(
                                Token(TokenType.IDENT, "x")
                            )
                        ),
                        Token(TokenType.ASTERISK),
                        InfixExpression(
                            LiteralExpression(
                                IdentifierLiteral(
                                    Token(TokenType.IDENT, "y"),
                                )
                            ),
                            Token(TokenType.MINUS),
                            LiteralExpression(
                                IntLiteral(
                                    Token(TokenType.INT, "3"),
                                    3
                                )
                            ),
                        )
                    )
                )
            )
        ]
    )
