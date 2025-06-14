"""
Error handling classes for SimpleLang syntax analyzer
"""

from typing import Optional

class SimpleLangError(Exception):
    """Base exception class for SimpleLang errors"""
    def __init__(self, message: str, line: int = 0, column: int = 0):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(self.message)
    
    def __str__(self):
        if self.line > 0:
            return f"Error at line {self.line}, column {self.column}: {self.message}"
        return f"Error: {self.message}"

class LexicalError(SimpleLangError):
    """Exception raised for lexical analysis errors"""
    def __init__(self, message: str, line: int = 0, column: int = 0, char: str = ""):
        self.char = char
        if char:
            message = f"Unexpected character '{char}': {message}"
        super().__init__(message, line, column)

class SyntaxError(SimpleLangError):
    """Exception raised for syntax analysis errors"""
    def __init__(self, message: str, line: int = 0, column: int = 0, expected: str = "", found: str = ""):
        self.expected = expected
        self.found = found
        
        if expected and found:
            message = f"Expected {expected}, but found {found}: {message}"
        elif expected:
            message = f"Expected {expected}: {message}"
        elif found:
            message = f"Unexpected {found}: {message}"
            
        super().__init__(message, line, column)

class SemanticError(SimpleLangError):
    """Exception raised for semantic analysis errors"""
    pass

class ParseError(SimpleLangError):
    """Exception raised for general parsing errors"""
    def __init__(self, message: str, line: int = 0, column: int = 0, token: Optional[str] = None):
        self.token = token
        if token:
            message = f"Parse error at token '{token}': {message}"
        super().__init__(message, line, column)

def format_error_context(source_lines: list, line_num: int, column: int, error_length: int = 1) -> str:
    """
    Format error context showing the problematic line with a pointer
    
    Args:
        source_lines: List of source code lines
        line_num: Line number (1-based)
        column: Column number (1-based)
        error_length: Length of the error span
    
    Returns:
        Formatted error context string
    """
    if not source_lines or line_num < 1 or line_num > len(source_lines):
        return ""
    
    line = source_lines[line_num - 1]
    line_str = f"{line_num:4d} | {line}"
    
    # Create pointer line
    pointer = " " * (7 + column - 1) + "^" + "~" * max(0, error_length - 1)
    
    context = f"\n{line_str}\n{pointer}\n"
    
    # Add surrounding lines for context
    result = ""
    if line_num > 1:
        result += f"{line_num-1:4d} | {source_lines[line_num - 2]}\n"
    
    result += context
    
    if line_num < len(source_lines):
        result += f"{line_num+1:4d} | {source_lines[line_num]}\n"
    
    return result

class ErrorReporter:
    """Utility class for reporting and collecting errors"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def report_error(self, error: SimpleLangError):
        """Report a syntax error"""
        self.errors.append(error)
    
    def report_warning(self, message: str, line: int = 0, column: int = 0):
        """Report a warning"""
        warning = SimpleLangError(f"Warning: {message}", line, column)
        self.warnings.append(warning)
    
    def has_errors(self) -> bool:
        """Check if any errors have been reported"""
        return len(self.errors) > 0
    
    def get_error_count(self) -> int:
        """Get the number of errors reported"""
        return len(self.errors)
    
    def get_warning_count(self) -> int:
        """Get the number of warnings reported"""
        return len(self.warnings)
    
    def print_errors(self, source_lines: Optional[list] = None):
        """Print all reported errors"""
        if not self.errors:
            print("No errors found.")
            return
        
        print(f"\nFound {len(self.errors)} error(s):\n")
        
        for i, error in enumerate(self.errors, 1):
            print(f"{i}. {error}")
            
            if source_lines and error.line > 0:
                context = format_error_context(source_lines, error.line, error.column)
                print(context)
    
    def print_warnings(self):
        """Print all reported warnings"""
        if not self.warnings:
            return
        
        print(f"\nFound {len(self.warnings)} warning(s):\n")
        
        for i, warning in enumerate(self.warnings, 1):
            print(f"{i}. {warning}")
    
    def clear(self):
        """Clear all errors and warnings"""
        self.errors.clear()
        self.warnings.clear()