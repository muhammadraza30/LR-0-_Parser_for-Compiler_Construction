"""
Syntax analyzer (parser) for SimpleLang using recursive descent parsing
"""

from typing import List, Optional, Union
from tokens import Token, TokenType
from grammar import *
from errors import SyntaxError, ParseError, ErrorReporter

class Parser:
    """Recursive descent parser for SimpleLang"""
    
    def __init__(self, tokens: List[Token], error_reporter: Optional[ErrorReporter] = None):
        self.tokens = tokens
        self.position = 0
        self.error_reporter = error_reporter or ErrorReporter()
        self.ast = None
    
    def current_token(self) -> Token:
        """Get the current token"""
        if self.position >= len(self.tokens):
            return self.tokens[-1]  # Return EOF token
        return self.tokens[self.position]
    
    def peek_token(self, offset: int = 1) -> Token:
        """Peek at token at current position + offset"""
        pos = self.position + offset
        if pos >= len(self.tokens):
            return self.tokens[-1]  # Return EOF token
        return self.tokens[pos]
    
    def advance(self) -> Token:
        """Advance to next token and return current token"""
        token = self.current_token()
        if self.position < len(self.tokens) - 1:
            self.position += 1
        return token
    
    def match(self, *token_types: TokenType) -> bool:
        """Check if current token matches any of the given types"""
        return self.current_token().type in token_types
    
    def consume(self, token_type: TokenType, error_message: str = "") -> Token:
        """Consume a token of the expected type or raise error"""
        if self.current_token().type == token_type:
            return self.advance()
        
        current = self.current_token()
        if not error_message:
            error_message = f"Expected {token_type.name}, found {current.type.name}"
        
        # More specific messages for common cases
        if token_type == TokenType.SEMICOLON:
            error_message = "Expected ';' at end of statement"
        elif token_type == TokenType.RIGHT_PAREN:
            error_message = "Expected ')' to close expression"
        elif token_type == TokenType.RIGHT_BRACE:
            error_message = "Expected '}' to close block"
        
        error = SyntaxError(
            error_message,
            current.line,
            current.column,
            expected=token_type.name,
            found=f"{current.type.name} '{current.value}'"
        )
        self.error_reporter.report_error(error)
        raise error
    
    def synchronize(self):
        """Synchronize parser after error (panic mode recovery)"""
        self.advance()
        
        while not self.match(TokenType.EOF):
            # Look for statement boundaries
            if self.current_token().type in {
                TokenType.SEMICOLON, TokenType.LEFT_BRACE, TokenType.RIGHT_BRACE,
                TokenType.IF, TokenType.WHILE, TokenType.FOR,
                TokenType.INT, TokenType.BOOL, TokenType.STRING
            }:
                return
            self.advance()
    
    def parse(self) -> Optional[Program]:
        """Parse the token stream and return AST"""
        try:
            self.ast = self.parse_program()
            return self.ast
        except Exception as e:
            if not isinstance(e, (SyntaxError, ParseError)):
                error = ParseError(f"Unexpected error during parsing: {str(e)}")
                self.error_reporter.report_error(error)
            return None
    
    def parse_program(self) -> Program:
        """Parse program: statement_list"""
        statements = []
        
        while not self.match(TokenType.EOF):
            try:
                stmt = self.parse_statement()
                if stmt:
                    statements.append(stmt)
            except (SyntaxError, ParseError):
                self.synchronize()
        
        return Program(statements, 1, 1)
    
    def parse_statement(self) -> Optional[Statement]:
        """Parse statement: declaration | assignment | control_statement | block | print_statement"""
        try:
            # Check for print statement (dikhao)
            if self.match(TokenType.PRINT):  # Assuming PRINT is the token type for 'dikhao'
                return self.parse_print_statement()
            # Check for declaration
            if self.match(TokenType.INT, TokenType.BOOL, TokenType.STRING):
                return self.parse_declaration()
            
            # Check for control statements
            if self.match(TokenType.IF):
                return self.parse_if_statement()
            
            if self.match(TokenType.WHILE):
                return self.parse_while_statement()
            
            if self.match(TokenType.FOR):
                return self.parse_for_statement()
            
            # Check for block
            if self.match(TokenType.LEFT_BRACE):
                return self.parse_block()
            
            # Check for assignment (identifier = ...)
            if self.match(TokenType.IDENTIFIER) and self.peek_token().type == TokenType.ASSIGN:
                return self.parse_assignment()
            
            # Check for input statement (likho)
            if self.match(TokenType.INPUT):  # Assuming INPUT is the token type for 'likho'
                return self.parse_input_statement()
            
            # If none of the above, it's an error
            current = self.current_token()
            error = SyntaxError(
                "Invalid statement",
                current.line,
                current.column,
                expected="declaration, assignment, control statement, or block",
                found=f"{current.type.name} '{current.value}'"
            )
            self.error_reporter.report_error(error)
            raise error
            
        except (SyntaxError, ParseError) as e:
            # Re-raise syntax errors
            raise e
        except Exception as e:
            current = self.current_token()
            error = ParseError(f"Error parsing statement: {str(e)}", current.line, current.column)
            self.error_reporter.report_error(error)
            raise error

    def parse_declaration(self) -> Union[DeclareNode, DeclareAndAssignNode]:
        """Parse variable declaration with or without initialization"""
        type_token = self.current_token()
        type_val = type_token.type
        self.advance()  # Consume type
        
        # Get identifier
        if not self.match(TokenType.IDENTIFIER):
            current = self.current_token()
            error = SyntaxError(
                "Expected identifier after type",
                current.line,
                current.column,
                expected="identifier",
                found=f"{current.type.name} '{current.value}'"
            )
            self.error_reporter.report_error(error)
            raise error
            
        identifier_token = self.current_token()
        identifier = identifier_token.value
        self.advance()  # Consume identifier
        
        # Handle initialization if present
        if self.match(TokenType.ASSIGN):
            self.advance()  # Consume '='
            expression = self.parse_expression()
            self.consume(TokenType.SEMICOLON, "Expected ';' after declaration")
            return DeclareAndAssignNode(
                type_val,
                identifier,
                expression,
                type_token.line,
                type_token.column
            )
        
        # Simple declaration without initialization
        self.consume(TokenType.SEMICOLON, "Expected ';' after declaration")
        return DeclareNode(
            type_val,
            identifier,
            type_token.line,
            type_token.column
        )

    def parse_assignment(self) -> Assignment:
        """Parse assignment: identifier '=' expression ';'"""
        identifier_token = self.advance()  # consume identifier
        self.consume(TokenType.ASSIGN, "Expected '=' in assignment")
        
        expression = self.parse_expression()
        
        self.consume(TokenType.SEMICOLON, "Expected ';' after assignment")
        
        return Assignment(
            identifier_token.value,
            expression,
            identifier_token.line,
            identifier_token.column
        )
    
    def parse_if_statement(self) -> IfStatement:
        """Parse if statement: 'if' '(' expression ')' statement ['else' statement]"""
        if_token = self.advance()  # consume 'if'
        
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'if'")
        condition = self.parse_expression()
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after if condition")
        
        then_statement = self.parse_statement()
        
        else_statement = None
        if self.match(TokenType.ELSE):
            self.advance()  # consume 'else'
            else_statement = self.parse_statement()
        
        return IfStatement(
            condition,
            then_statement,
            else_statement,
            if_token.line,
            if_token.column
        )
    
    def parse_while_statement(self) -> WhileStatement:
        """Parse while statement: 'while' '(' expression ')' statement"""
        while_token = self.advance()  # consume 'while'
        
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'while'")
        condition = self.parse_expression()
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after while condition")
        
        body = self.parse_statement()
        
        return WhileStatement(
            condition,
            body,
            while_token.line,
            while_token.column
        )
    
    def parse_for_statement(self) -> ForStatement:
        """Parse for statement: 'for' '(' (declaration | assignment) ';' expression ';' assignment ')' statement"""
        for_token = self.advance()  # consume 'for'
        
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'for'")
        
        # Parse initialization (can be declaration or assignment)
        if self.match(TokenType.INT, TokenType.BOOL, TokenType.STRING):
            init_decl = self.parse_declaration()
            # Convert declaration to assignment if it has initialization
            if isinstance(init_decl, DeclareAndAssignNode):
                init = Assignment(
                    init_decl.identifier,
                    init_decl.expression,
                    init_decl.line,
                    init_decl.column
                )
            else:
                # Handle case where there's no initialization
                current = self.current_token()
                error = SyntaxError(
                    "For loop initialization must include assignment",
                    current.line,
                    current.column
                )
                self.error_reporter.report_error(error)
                raise error
        else:
            init = self.parse_assignment_without_semicolon()
        
        # Parse condition
        condition = self.parse_expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after for loop condition")
        
        # Parse update (must be assignment)
        if not self.match(TokenType.IDENTIFIER):
            current = self.current_token()
            error = SyntaxError(
                "Expected assignment in for loop update",
                current.line,
                current.column
            )
            self.error_reporter.report_error(error)
            raise error
        
        update = self.parse_assignment_without_semicolon()
        
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after for loop header")
        
        body = self.parse_statement()
        
        return ForStatement(
            init,
            condition,
            update,
            body,
            for_token.line,
            for_token.column
        )
    
    def parse_assignment_without_semicolon(self) -> Assignment:
        """Parse assignment without consuming the semicolon"""
        identifier_token = self.advance()  # consume identifier
        self.consume(TokenType.ASSIGN, "Expected '=' in assignment")
        expression = self.parse_expression()
        
        return Assignment(
            identifier_token.value,
            expression,
            identifier_token.line,
            identifier_token.column
        )
    
    def parse_block(self) -> Block:
        """Parse block: '{' [statement_list] '}'"""
        left_brace = self.advance()  # consume '{'
        
        statements = []
        while not self.match(TokenType.RIGHT_BRACE, TokenType.EOF):
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        
        self.consume(TokenType.RIGHT_BRACE, "Expected '}' to close block")
        
        return Block(statements, left_brace.line, left_brace.column)
    
    def parse_expression(self) -> Expression:
        """Parse expression: logical_or"""
        return self.parse_logical_or()
    
    def parse_logical_or(self) -> Expression:
        """Parse logical_or: logical_and ('||' logical_and)*"""
        expr = self.parse_logical_and()
        
        while self.match(TokenType.OR):
            operator_token = self.advance()
            right = self.parse_logical_and()
            expr = BinaryExpression(
                expr,
                operator_token.type,
                right,
                expr.line,
                expr.column
            )
        
        return expr
    
    def parse_logical_and(self) -> Expression:
        """Parse logical_and: equality ('&&' equality)*"""
        expr = self.parse_equality()
        
        while self.match(TokenType.AND):
            operator_token = self.advance()
            right = self.parse_equality()
            expr = BinaryExpression(
                expr,
                operator_token.type,
                right,
                expr.line,
                expr.column
            )
        
        return expr
    
    def parse_equality(self) -> Expression:
        """Parse equality: relational (('==' | '!=') relational)*"""
        expr = self.parse_relational()
        
        while self.match(TokenType.EQUAL, TokenType.NOT_EQUAL):
            operator_token = self.advance()
            right = self.parse_relational()
            expr = BinaryExpression(
                expr,
                operator_token.type,
                right,
                expr.line,
                expr.column
            )
        
        return expr
    
    def parse_relational(self) -> Expression:
        """Parse relational: additive (('<' | '>' | '<=' | '>=') additive)*"""
        expr = self.parse_additive()
        
        while self.match(TokenType.LESS_THAN, TokenType.GREATER_THAN, 
                         TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL):
            operator_token = self.advance()
            right = self.parse_additive()
            expr = BinaryExpression(
                expr,
                operator_token.type,
                right,
                expr.line,
                expr.column
            )
        
        return expr
    
    def parse_additive(self) -> Expression:
        """Parse additive: multiplicative (('+' | '-') multiplicative)*"""
        expr = self.parse_multiplicative()
        
        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator_token = self.advance()
            right = self.parse_multiplicative()
            expr = BinaryExpression(
                expr,
                operator_token.type,
                right,
                expr.line,
                expr.column
            )
        
        return expr
    
    def parse_multiplicative(self) -> Expression:
        """Parse multiplicative: unary (('*' | '/' | '%') unary)*"""
        expr = self.parse_unary()
        
        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            operator_token = self.advance()
            right = self.parse_unary()
            expr = BinaryExpression(
                expr,
                operator_token.type,
                right,
                expr.line,
                expr.column
            )
        
        return expr
    
    def parse_unary(self) -> Expression:
        """Parse unary: ('!' | '-') unary | primary"""
        if self.match(TokenType.NOT, TokenType.MINUS):
            operator_token = self.advance()
            operand = self.parse_unary()
            return UnaryExpression(
                operator_token.type,
                operand,
                operator_token.line,
                operator_token.column
            )
        
        return self.parse_primary()
    
    def parse_primary(self) -> Expression:
        """Parse primary: identifier | integer | boolean | string | '(' expression ')'"""
        current = self.current_token()
        
        if self.match(TokenType.IDENTIFIER):
            token = self.advance()
            return Identifier(token.value, token.line, token.column)
        
        if self.match(TokenType.INTEGER):
            token = self.advance()
            return IntegerLiteral(token.value, token.line, token.column)
        
        if self.match(TokenType.TRUE):
            token = self.advance()
            return BooleanLiteral(True, token.line, token.column)
        
        if self.match(TokenType.FALSE):
            token = self.advance()
            return BooleanLiteral(False, token.line, token.column)
        
        if self.match(TokenType.STRING_LITERAL):
            token = self.advance()
            return StringLiteral(token.value, token.line, token.column)
        
        if self.match(TokenType.LEFT_PAREN):
            self.advance()  # consume '('
            expr = self.parse_expression()
            self.consume(TokenType.RIGHT_PAREN, "Expected ')' after expression")
            return expr
        
        # If we reach here, it's an error
        error = SyntaxError(
            "Expected expression",
            current.line,
            current.column,
            expected="identifier, literal, or '('",
            found=f"{current.type.name} '{current.value}'"
        )
        self.error_reporter.report_error(error)
        raise error

    def parse_print_statement(self) -> PrintNode:
        """Parse print statement: dikhao ( expression_list ) ;"""
        dikhao_token = self.advance()  # consume 'dikhao'
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'dikhao'")
        
        expressions = []
        # Parse first expression
        expressions.append(self.parse_expression())
        
        # Parse additional expressions separated by commas
        while self.match(TokenType.COMMA):
            self.advance()  # consume comma
            expressions.append(self.parse_expression())
        
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after print arguments")
        self.consume(TokenType.SEMICOLON, "Expected ';' after print statement")
        
        return PrintNode(
            expressions,
            dikhao_token.line,
            dikhao_token.column
        )

    def parse_input_statement(self) -> InputNode:
        """Parse input statement: likho ( identifier ) ;"""
        likho_token = self.advance()  # consume 'likho'
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'likho'")
        
        if not self.match(TokenType.IDENTIFIER):
            current = self.current_token()
            error = SyntaxError(
                "Expected identifier in input statement",
                current.line,
                current.column,
                expected="identifier",
                found=f"{current.type.name} '{current.value}'"
            )
            self.error_reporter.report_error(error)
            raise error
        
        identifier_token = self.advance()  # consume identifier
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after identifier")
        self.consume(TokenType.SEMICOLON, "Expected ';' after input statement")
        
        return InputNode(
            identifier_token.value,
            likho_token.line,
            likho_token.column
        )