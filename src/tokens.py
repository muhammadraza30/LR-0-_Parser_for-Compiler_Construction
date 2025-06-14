"""
Token definitions for SimpleLang syntax analyzer
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Any, Optional

class TokenType(Enum):
    # Keywords
    INT = auto()
    BOOL = auto()
    STRING = auto()
    IF = auto()
    ELSE = auto()
    FOR = auto()
    WHILE = auto()
    TRUE = auto()
    FALSE = auto()
    PRINT = auto()
    
    # Operators
    PLUS = auto()           # +
    MINUS = auto()          # -
    MULTIPLY = auto()       # *
    DIVIDE = auto()  
    MODULO = auto()       # /
    ASSIGN = auto()         # =
    LESS_THAN = auto()      # <
    GREATER_THAN = auto()   # >
    LESS_EQUAL = auto()     # <=
    GREATER_EQUAL = auto()  # >=
    EQUAL = auto()          # ==
    NOT_EQUAL = auto()      # !=
    AND = auto()            # &&
    OR = auto()             # ||
    NOT = auto()            # !
    
    # Symbols
    SEMICOLON = auto()      # ;
    LEFT_BRACE = auto()     # {
    RIGHT_BRACE = auto()    # }
    LEFT_PAREN = auto()     # (
    RIGHT_PAREN = auto()    # )
    COMMA = auto()          # ,
    
    # Literals and Identifiers
    IDENTIFIER = auto()     # variable names
    INTEGER = auto()        # integer literals
    STRING_LITERAL = auto() # string literals
    
    # Special tokens
    EOF = auto()            # End of file
    NEWLINE = auto()        # New line (for error reporting)
    
    def __str__(self):
        return self.name

@dataclass
class Token:
    """Represents a single token in the source code"""
    type: TokenType
    value: Any
    line: int
    column: int
    
    def __str__(self):
        return f"Token({self.type}, '{self.value}', {self.line}:{self.column})"
    
    def __repr__(self):
        return self.__str__()

# Keywords mapping
KEYWORDS = {
    'int': TokenType.INT,
    'bool': TokenType.BOOL,
    'string': TokenType.STRING,
    'if': TokenType.IF,
    'else': TokenType.ELSE,
    'for': TokenType.FOR,
    'while': TokenType.WHILE,
    'true': TokenType.TRUE,
    'false': TokenType.FALSE,
    'dikhao': TokenType.PRINT  # Add dikhao keyword
}

# Single character operators/symbols
SINGLE_CHAR_TOKENS = {
    '+': TokenType.PLUS,
    '-': TokenType.MINUS,
    '*': TokenType.MULTIPLY,
    '/': TokenType.DIVIDE,
    '%': TokenType.MODULO,
    '=': TokenType.ASSIGN,
    '<': TokenType.LESS_THAN,
    '>': TokenType.GREATER_THAN,
    '!': TokenType.NOT,
    ';': TokenType.SEMICOLON,
    '{': TokenType.LEFT_BRACE,
    '}': TokenType.RIGHT_BRACE,
    '(': TokenType.LEFT_PAREN,
    ')': TokenType.RIGHT_PAREN,
    ',': TokenType.COMMA,
}

# Two character operators
DOUBLE_CHAR_TOKENS = {
    '<=': TokenType.LESS_EQUAL,
    '>=': TokenType.GREATER_EQUAL,
    '==': TokenType.EQUAL,
    '!=': TokenType.NOT_EQUAL,
    '&&': TokenType.AND,
    '||': TokenType.OR,
}