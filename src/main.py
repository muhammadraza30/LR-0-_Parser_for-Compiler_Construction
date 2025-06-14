import sys
import os
from typing import Optional
from lexer import Lexer
from parser import Parser
from errors import ErrorReporter, format_error_context
from grammar import Program

class SimpleLangAnalyzer:
    """Main analyzer class that coordinates lexing and parsing"""
    
    def __init__(self):
        self.error_reporter = ErrorReporter()
        self.source_lines = []
        self.ast = None
    
    def analyze_file(self, filename: str) -> bool:
        """Analyze a SimpleLang source file"""
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                source = file.read()
            
            return self.analyze_source(source, filename)
            
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
            return False
        except Exception as e:
            print(f"Error reading file '{filename}': {str(e)}")
            return False
    
    def analyze_source(self, source: str, filename: str = "<source>") -> bool:
        """Analyze SimpleLang source code"""
        self.error_reporter.clear()
        self.source_lines = source.splitlines()
        
        print(f"Analyzing {filename}...")
        print("=" * 50)
        
        # Lexical Analysis
        print("Phase 1: Lexical Analysis")
        lexer = Lexer(source, self.error_reporter)
        tokens = lexer.tokenize()
        
        if self.error_reporter.has_errors():
            print(f"Lexical analysis failed with {self.error_reporter.get_error_count()} error(s).")
            self.error_reporter.print_errors(self.source_lines)
            return False
        
        print(f"Lexical analysis completed successfully. Generated {len(tokens)} tokens.")
        
        # Syntax Analysis
        print("\nPhase 2: Syntax Analysis")
        parser = Parser(tokens, self.error_reporter)
        self.ast = parser.parse()
        
        if self.error_reporter.has_errors():
            print(f"Syntax analysis failed with {self.error_reporter.get_error_count()} error(s).")
            self.error_reporter.print_errors(self.source_lines)
            return False
        
        print("Syntax analysis completed successfully!")
        
        # Print warnings if any
        if self.error_reporter.get_warning_count() > 0:
            self.error_reporter.print_warnings()
        
        return True
    
    def print_tokens(self, source: str):
        """Print tokens for debugging"""
        lexer = Lexer(source, self.error_reporter)
        tokens = lexer.tokenize()
        
        print("Tokens:")
        print("-" * 50)
        for i, token in enumerate(tokens):
            if token.type.name != 'EOF':
                print(f"{i:3d}: {token}")

def print_usage():
    """Print usage information"""
    print("SimpleLang Syntax Analyzer")
    print("Usage:")
    print("  python main.py <file.sl>           - Analyze a SimpleLang file")
    print("  python main.py --tokens <file.sl>  - Show tokens only")
    print("  python main.py --interactive       - Interactive mode")

def interactive_mode():
    """Interactive mode for testing code snippets"""
    analyzer = SimpleLangAnalyzer()
    
    print("SimpleLang Interactive Mode")
    print("Enter SimpleLang code (type 'exit' to quit, 'help' for commands)")
    print("-" * 50)
    
    while True:
        try:
            print("\n> ", end="")
            line = input().strip()
            
            if line.lower() in ['exit', 'quit']:
                break
            elif line.lower() == 'help':
                print("Commands:")
                print("  exit/quit - Exit interactive mode")
                print("  help      - Show this help")
                print("  tokens    - Show tokens for last input")
                continue
            elif line.lower() == 'tokens':
                if hasattr(interactive_mode, 'last_source'):
                    analyzer.print_tokens(interactive_mode.last_source)
                else:
                    print("No previous input.")
                continue
            elif not line:
                continue
            
            # Collect multi-line input
            source = line
            if not line.endswith(';') and not line.endswith('}'):
                print("... ", end="")
                while True:
                    next_line = input().strip()
                    if not next_line:
                        break
                    source += '\n' + next_line
                    if next_line.endswith(';') or next_line.endswith('}'):
                        break
                    print("... ", end="")
            
            interactive_mode.last_source = source
            success = analyzer.analyze_source(source, "<interactive>")
            
            if success:
                print("✓ Code is syntactically correct!")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            print("\nGoodbye!")
            break

def resolve_test_file_path(filename: str) -> str:
    """Resolve the path to a test file in the tests/test_cases folder."""
    base_dir = os.path.dirname(__file__)  # Get the directory of main.py
    test_cases_dir = os.path.abspath(os.path.join(base_dir, '..', 'tests', 'test_cases'))  # Absolute path to test_cases
    return os.path.join(test_cases_dir, filename)

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print_usage()
        return 1
    
    analyzer = SimpleLangAnalyzer()
    
    if sys.argv[1] == '--interactive':
        interactive_mode()
        return 0
    
    if sys.argv[1] == '--tokens':
        # Show tokens only
        if len(sys.argv) < 3:
            print_usage()
            return 1
        
        filename = sys.argv[2]
        if not os.path.exists(filename):
            # Resolve path if file is in the test_cases folder
            filename = resolve_test_file_path(filename)
            if not os.path.exists(filename):
                print(f"Error: File '{filename}' does not exist.")
                sys.exit(1)
        
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                source = file.read()
            analyzer.print_tokens(source)
        except Exception as e:
            print(f"Error: {str(e)}")
            return 1
    
    else:
        # Regular analysis
        filename = sys.argv[1]
        if not os.path.exists(filename):
            # Resolve path if file is in the test_cases folder
            filename = resolve_test_file_path(filename)
            if not os.path.exists(filename):
                print(f"Error: File '{filename}' does not exist.")
                sys.exit(1)
        
        success = analyzer.analyze_file(filename)
        return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())