from typing import List
from pycompiler.lexer import Lexer, Token, TokenType

def assert_output(test_input: str, exp_output: List[Token]):
    lexer = Lexer(test_input)
    for exp_token in exp_output:
        assert lexer.next_token() == exp_token

def test_simple_tokens():
    assert_output(
        "+   - \n \n /*", 
        [Token(TokenType.PLUS), Token(TokenType.MINUS), Token(TokenType.SLASH), Token(TokenType.ASTERISK)]
    )

def test_ident_tokens():
    assert_output(
        "adam    *ragausea",
        [Token(TokenType.IDENT, "adam"), Token(TokenType.ASTERISK), Token(TokenType.IDENT, "ragausea")]
    )

def test_int_tokens():
    assert_output(
        "342    *1903",
        [Token(TokenType.INT, "342"), Token(TokenType.ASTERISK), Token(TokenType.INT, "1903")]
    )

def test_string_tokens():
    assert_output(
        "\"342 string\n test\"    * \"1903\"",
        [Token(TokenType.STRING, "342 string\n test"), Token(TokenType.ASTERISK), Token(TokenType.STRING, "1903")]
    )

def test_mixed_tokens():
    assert_output(
        "342    *adam / test102",
        [
            Token(TokenType.INT, "342"), 
            Token(TokenType.ASTERISK), 
            Token(TokenType.IDENT, "adam"), 
            Token(TokenType.SLASH), 
            Token(TokenType.IDENT, "test102")
        ]
    )

def test_keyword_tokens():
    assert_output(
        "return 203 if adam else let",
        [
            Token(TokenType.RETURN), 
            Token(TokenType.INT, "203"), 
            Token(TokenType.IF), 
            Token(TokenType.IDENT, "adam"), 
            Token(TokenType.ELSE), 
            Token(TokenType.LET)
        ]
    )

def test_twochar_tokens():
    assert_output(
        "! != = ==",
        [
            Token(TokenType.BANG), 
            Token(TokenType.NOT_EQ), 
            Token(TokenType.ASSIGN), 
            Token(TokenType.EQ), 
        ]
    )
