"""
Lexical analyzer for SimpleLang syntax analyzer
"""

import re
from typing import List, Optional, Iterator
from tokens import Token, TokenType, KEYWORDS, SINGLE_CHAR_TOKENS, DOUBLE_CHAR_TOKENS
from errors import LexicalError, ErrorReporter

class Lexer:
    """Lexical analyzer for SimpleLang"""
    
    def __init__(self, source: str, error_reporter: Optional[ErrorReporter] = None):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens = []
        self.error_reporter = error_reporter or ErrorReporter()
        
        # Precompiled regex patterns
        self.identifier_pattern = re.compile(r'[a-zA-Z][a-zA-Z0-9_]*')
        self.integer_pattern = re.compile(r'\d+')
        self.string_pattern = re.compile(r'"([^"\\]|\\.)*"')
        self.whitespace_pattern = re.compile(r'[ \t]+')
        self.comment_pattern = re.compile(r'//.*')
    
    def current_char(self) -> Optional[str]:
        """Get the current character"""
        if self.position >= len(self.source):
            return None
        return self.source[self.position]
    
    def peek_char(self, offset: int = 1) -> Optional[str]:
        """Peek at the character at current position + offset"""
        pos = self.position + offset
        if pos >= len(self.source):
            return None
        return self.source[pos]
    
    def advance(self) -> Optional[str]:
        """Advance to the next character and return the current one"""
        if self.position >= len(self.source):
            return None
        
        char = self.source[self.position]
        self.position += 1
        
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        
        return char
    
    def skip_whitespace(self):
        """Skip whitespace characters except newlines"""
        while self.current_char() and self.current_char() in ' \t':
            self.advance()
    
    def skip_comment(self):
        """Skip single-line comments starting with //"""
        if self.current_char() == '/' and self.peek_char() == '/':
            # Skip until end of line
            while self.current_char() and self.current_char() != '\n':
                self.advance()
    
    def read_string_literal(self) -> str:
        """Read a string literal enclosed in double quotes"""
        start_pos = self.position
        start_col = self.column
        
        if self.current_char() != '"':
            raise LexicalError("Expected '\"' at start of string", self.line, self.column)
        
        self.advance()  # Skip opening quote
        value = ''
        
        while self.current_char() and self.current_char() != '"':
            char = self.current_char()
            
            if char == '\\':
                # Handle escape sequences
                self.advance()
                next_char = self.current_char()
                
                if next_char is None:
                    raise LexicalError("Unterminated string literal", self.line, start_col)
                
                if next_char == 'n':
                    value += '\n'
                elif next_char == 't':
                    value += '\t'
                elif next_char == 'r':
                    value += '\r'
                elif next_char == '\\':
                    value += '\\'
                elif next_char == '"':
                    value += '"'
                else:
                    value += next_char
                
                self.advance()
            elif char == '\n':
                raise LexicalError("Unterminated string literal", self.line, start_col)
            else:
                value += char
                self.advance()
        
        if self.current_char() != '"':
            raise LexicalError("Unterminated string literal", self.line, start_col)
        
        self.advance()  # Skip closing quote
        return value
    
    def read_number(self) -> int:
        """Read an integer literal"""
        value = ''
        
        while self.current_char() and self.current_char().isdigit():
            value += self.current_char()
            self.advance()
        
        return int(value)
    
    def read_identifier(self) -> str:
        """Read an identifier or keyword"""
        value = ''
        
        # First character must be a letter
        if not self.current_char().isalpha():
            raise LexicalError("Identifier must start with a letter", self.line, self.column)
        
        while (self.current_char() and 
               (self.current_char().isalnum() or self.current_char() == '_')):
            value += self.current_char()
            self.advance()
        
        return value
    
    def read_operator(self) -> str:
        """Read an operator (single or double character)"""
        char = self.current_char()
        next_char = self.peek_char()
        
        # Check for double-character operators
        if next_char and (char + next_char) in DOUBLE_CHAR_TOKENS:
            two_char = char + next_char
            self.advance()
            self.advance()
            return two_char
        
        # Single character operator
        if char in SINGLE_CHAR_TOKENS:
            self.advance()
            return char
        
        raise LexicalError(f"Unknown operator", self.line, self.column, char)
    
    def tokenize(self) -> List[Token]:
        """Tokenize the entire source code"""
        self.tokens = []
        
        while self.position < len(self.source):
            try:
                self.skip_whitespace()
                
                char = self.current_char()
                if char is None:
                    break
                
                token_line = self.line
                token_column = self.column
                
                # Handle newlines
                if char == '\n':
                    self.advance()
                    continue
                
                # Handle comments
                if char == '/' and self.peek_char() == '/':
                    self.skip_comment()
                    continue
                
                # Handle string literals
                if char == '"':
                    try:
                        value = self.read_string_literal()
                        token = Token(TokenType.STRING_LITERAL, value, token_line, token_column)
                        self.tokens.append(token)
                    except LexicalError as e:
                        self.error_reporter.report_error(e)
                        # Skip the problematic character and continue
                        self.advance()
                    continue
                
                # Handle numbers
                if char.isdigit():
                    value = self.read_number()
                    token = Token(TokenType.INTEGER, value, token_line, token_column)
                    self.tokens.append(token)
                    continue
                
                # Handle identifiers and keywords
                if char.isalpha():
                    value = self.read_identifier()
                    token_type = KEYWORDS.get(value, TokenType.IDENTIFIER)
                    token = Token(token_type, value, token_line, token_column)
                    self.tokens.append(token)
                    continue
                
                # Handle operators and symbols
                if char in SINGLE_CHAR_TOKENS or (char + (self.peek_char() or '')) in DOUBLE_CHAR_TOKENS:
                    try:
                        value = self.read_operator()
                        if value in DOUBLE_CHAR_TOKENS:
                            token_type = DOUBLE_CHAR_TOKENS[value]
                        else:
                            token_type = SINGLE_CHAR_TOKENS[value]
                        token = Token(token_type, value, token_line, token_column)
                        self.tokens.append(token)
                    except LexicalError as e:
                        self.error_reporter.report_error(e)
                        self.advance()
                    continue
                
                # Unknown character
                error = LexicalError(f"Unexpected character", self.line, self.column, char)
                self.error_reporter.report_error(error)
                self.advance()
                
            except Exception as e:
                error = LexicalError(f"Unexpected error during tokenization: {str(e)}", 
                                   self.line, self.column)
                self.error_reporter.report_error(error)
                self.advance()
        
        # Add EOF token
        self.tokens.append(Token(TokenType.EOF, '', self.line, self.column))
        return self.tokens
    
    def get_tokens(self) -> List[Token]:
        """Get the list of tokens (tokenize if not already done)"""
        if not self.tokens:
            self.tokenize()
        return self.tokens
    
    def print_tokens(self):
        """Print all tokens for debugging"""
        if not self.tokens:
            self.tokenize()
        
        print("Tokens:")
        print("-" * 50)
        for i, token in enumerate(self.tokens):
            print(f"{i:3d}: {token}")

# Utility function for quick tokenization
def tokenize(source: str, error_reporter: Optional[ErrorReporter] = None) -> List[Token]:
    """Tokenize source code and return list of tokens"""
    lexer = Lexer(source, error_reporter)
    return lexer.tokenize()