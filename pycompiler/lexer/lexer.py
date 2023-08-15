from enum import Enum
from typing import Optional


class TokenType(Enum):
    # Extras
    EOF = "EOF"
    ILLEGAL = "ILLEGAL"

    # Identifiers and literals
    IDENT = "IDENT"
    STRING = "STRING"
    INT = "INT"

    # Operators
    ASSIGN = "="
    PLUS = "+"
    MINUS = "-"
    BANG = "!"
    ASTERISK = "*"
    SLASH = "/"
    LT = "<"
    GT = ">"
    EQ = "=="
    NOT_EQ = "!="

    # Delimiters
    COMMA = ","
    COLON = ":"
    SEMICOLON = ";"
    DB_QUOTE = '"'

    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    LBRACKET = "["
    RBRACKET = "]"

    # Keywords
    FUNCTION = "fn"
    LET = "let"
    TRUE = "true"
    FALSE = "false"
    IF = "if"
    ELSE = "else"
    RETURN = "return"


class Token:
    def __init__(self, token_type: TokenType, token_value: Optional[str] = None):
        self.token_type: Token = token_type
        if token_value:
            self.token_value: str = token_value
        else:
            self.token_value: str = token_type.value

    def __eq__(self, other):
        return (
            self.token_type == other.token_type
            and self.token_value == other.token_value
        )

    def __repr__(self):
        return f"<Token: token_type={self.token_type}, token_value={self.token_value}>"


class Lexer:
    def __init__(self, input_string: str):
        self.input_string: str = input_string
        # position of the last byte read
        self.position: int = 0
        # position of the next byte read
        self.read_position: int = 0

        self.cur_byte: char = ""

        # Load up the first token into cur_byte
        self._read_char()

    def next_token(self) -> Token:
        self._skip_whitespace()

        token: Optional[Token] = None

        # More complex tokens
        if self.cur_byte == TokenType.DB_QUOTE.value:
            token = Token(TokenType.STRING, self._read_string())
        elif self._is_letter(self.cur_byte):
            identifier = self._read_identifier()
            for token_type in TokenType:
                if identifier == token_type.value:
                    token = Token(token_type)
                    break
            if not token:
                token = Token(TokenType.IDENT, identifier)
        elif self._is_number(self.cur_byte):
            token = Token(TokenType.INT, self._read_int())
        else:
            # Matching up simple tokens
            for token_type in TokenType:
                if self.cur_byte == token_type.value:
                    token = Token(token_type)
                    break

            # Two char tokens
            if (
                self.cur_byte == TokenType.ASSIGN.value
                and self._peek_char() == TokenType.ASSIGN.value
            ):
                self._read_char()
                token = Token(TokenType.EQ)
            elif (
                self.cur_byte == TokenType.BANG.value
                and self._peek_char() == TokenType.ASSIGN.value
            ):
                self._read_char()
                token = Token(TokenType.NOT_EQ)

        if not token:
            token = Token(TokenType.ILLEGAL)

        # Advance to next char
        self._read_char()

        return token

    def _read_char(self):
        if self.read_position >= len(self.input_string):
            self.cur_byte = "EOF"
        else:
            self.cur_byte = self.input_string[self.read_position]
        self.position = self.read_position
        self.read_position += 1

    def _peek_char(self) -> str:
        if self.read_position >= len(self.input_string):
            return "EOF"
        else:
            return self.input_string[self.read_position]

    def _read_identifier(self) -> str:
        identifier = self.cur_byte
        while self._is_letter(self._peek_char()) or self._is_number(self._peek_char()):
            self._read_char()
            identifier += self.cur_byte
        return identifier

    def _read_int(self) -> str:
        number = self.cur_byte
        while self._is_number(self._peek_char()):
            self._read_char()
            number += self.cur_byte
        return number

    def _read_string(self) -> str:
        # Advance first quote
        self._read_char()

        string = ""
        while self.cur_byte != TokenType.DB_QUOTE.value:
            string += self.cur_byte
            self._read_char()

        return string

    def _is_letter(self, value):
        return (
            (value >= "a" and value <= "z")
            or (value >= "A" and value <= "Z")
            or value == "_"
        ) and value != TokenType.EOF.value

    def _is_number(self, value):
        return (value >= "0" and value <= "9") and value != TokenType.EOF.value

    def _skip_whitespace(self):
        while self.cur_byte in [" ", "\t", "\n", "\r"]:
            self._read_char()
