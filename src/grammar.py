"""
Grammar definitions for SimpleLang syntax analyzer
BNF/EBNF grammar specification
"""

from dataclasses import dataclass
from typing import List, Optional, Union
from tokens import TokenType

# Grammar specification in BNF format
SIMPLELANG_BNF_GRAMMAR = """
# SimpleLang Grammar Specification (BNF)

<program>           ::= <statement_list>

<statement_list>    ::= <statement> <statement_list> | <statement>

<statement>         ::= <declaration> | <assignment> | <control_statement> | <block>

<declaration>       ::= <type> <identifier> ';' | <type> <identifier> '=' <expression> ';'

<assignment>        ::= <identifier> '=' <expression> ';'

<control_statement> ::= <if_statement> | <while_statement> | <for_statement>

<if_statement>      ::= 'if' '(' <expression> ')' <statement> 
                      | 'if' '(' <expression> ')' <statement> 'else' <statement>

<while_statement>   ::= 'while' '(' <expression> ')' <statement>

<for_statement>     ::= 'for' '(' (<declaration> | <assignment>) ';' <expression> ';' <assignment> ')' <statement>

<block>             ::= '{' <statement_list> '}' | '{' '}'

<expression>        ::= <logical_or>

<logical_or>        ::= <logical_and> | <logical_or> '||' <logical_and>

<logical_and>       ::= <equality> | <logical_and> '&&' <equality>

<equality>          ::= <relational> | <equality> '==' <relational> | <equality> '!=' <relational>

<relational>        ::= <additive> | <relational> '<' <additive> | <relational> '>' <additive>
                      | <relational> '<=' <additive> | <relational> '>=' <additive>

<additive>          ::= <multiplicative> | <additive> '+' <multiplicative> | <additive> '-' <multiplicative>

<multiplicative>    ::= <unary> | <multiplicative> '*' <unary> | <multiplicative> '/' <unary>

<unary>             ::= <primary> | '!' <unary> | '-' <unary>

<primary>           ::= <identifier> | <integer> | <boolean> | <string> | '(' <expression> ')'

<type>              ::= 'int' | 'bool' | 'string'

<identifier>        ::= [a-zA-Z][a-zA-Z0-9_]*

<integer>           ::= [0-9]+

<boolean>           ::= 'true' | 'false'

<string>            ::= '"' .* '"'
"""

# AST Node Types
@dataclass
class ASTNode:
    """Base class for all AST nodes"""
    line: int
    column: int

@dataclass
class Program(ASTNode):
    """Root node of the AST"""
    statements: List['Statement']

@dataclass
class Statement(ASTNode):
    """Base class for all statements"""
    pass

@dataclass
class Declaration(Statement):
    """Variable declaration: type identifier;"""
    type: TokenType  # INT, BOOL, STRING
    identifier: str

@dataclass
class Assignment(Statement):
    """Assignment statement: identifier = expression;"""
    identifier: str
    expression: 'Expression'

@dataclass
class IfStatement(Statement):
    """If statement: if (condition) then_stmt [else else_stmt]"""
    condition: 'Expression'
    then_statement: Statement
    else_statement: Optional[Statement] = None

@dataclass
class WhileStatement(Statement):
    """While loop: while (condition) body"""
    condition: 'Expression'
    body: Statement

@dataclass
class ForStatement(Statement):
    """For loop: for (init; condition; update) body"""
    init: Assignment
    condition: 'Expression'
    update: Assignment
    body: Statement

@dataclass
class Block(Statement):
    """Block statement: { statements }"""
    statements: List[Statement]

@dataclass
class Expression(ASTNode):
    """Base class for all expressions"""
    pass

@dataclass
class BinaryExpression(Expression):
    """Binary expression: left operator right"""
    left: Expression
    operator: TokenType
    right: Expression

@dataclass
class UnaryExpression(Expression):
    """Unary expression: operator operand"""
    operator: TokenType
    operand: Expression

@dataclass
class Identifier(Expression):
    """Identifier expression"""
    name: str

@dataclass
class IntegerLiteral(Expression):
    """Integer literal expression"""
    value: int

@dataclass
class BooleanLiteral(Expression):
    """Boolean literal expression"""
    value: bool

@dataclass
class StringLiteral(Expression):
    """String literal expression"""
    value: str
@dataclass
class DeclareNode(Statement):
    """Variable declaration without initialization"""
    type_token: TokenType
    identifier: str

@dataclass 
class DeclareAndAssignNode(Statement):
    """Variable declaration with initialization"""
    type_token: TokenType
    identifier: str
    expression: Expression

@dataclass
class PrintNode(Statement):
    """Print statement (dikhao)"""
    expressions: List[Expression]
# Operator precedence levels (higher number = higher precedence)
OPERATOR_PRECEDENCE = {
    TokenType.OR: 1,
    TokenType.AND: 2,
    TokenType.EQUAL: 3,
    TokenType.NOT_EQUAL: 3,
    TokenType.LESS_THAN: 4,
    TokenType.GREATER_THAN: 4,
    TokenType.LESS_EQUAL: 4,
    TokenType.GREATER_EQUAL: 4,
    TokenType.PLUS: 5,
    TokenType.MINUS: 5,
    TokenType.MULTIPLY: 6,
    TokenType.DIVIDE: 6,
    TokenType.MODULO: 6,
    TokenType.NOT: 7,  # Unary operators have highest precedence
}

# Grammar validation sets
DECLARATION_TYPES = {TokenType.INT, TokenType.BOOL, TokenType.STRING}
BINARY_OPERATORS = {
    TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY, TokenType.DIVIDE,TokenType.MODULO,
    TokenType.LESS_THAN, TokenType.GREATER_THAN, TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL,
    TokenType.EQUAL, TokenType.NOT_EQUAL, TokenType.AND, TokenType.OR
}
UNARY_OPERATORS = {TokenType.NOT, TokenType.MINUS}
COMPARISON_OPERATORS = {
    TokenType.LESS_THAN, TokenType.GREATER_THAN, TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL,
    TokenType.EQUAL, TokenType.NOT_EQUAL
}
LOGICAL_OPERATORS = {TokenType.AND, TokenType.OR}
ARITHMETIC_OPERATORS = {TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY, TokenType.DIVIDE,TokenType.MODULO}

def is_declaration_type(token_type: TokenType) -> bool:
    """Check if token type is a valid declaration type"""
    return token_type in DECLARATION_TYPES

def is_binary_operator(token_type: TokenType) -> bool:
    """Check if token type is a binary operator"""
    return token_type in BINARY_OPERATORS

def is_unary_operator(token_type: TokenType) -> bool:
    """Check if token type is a unary operator"""
    return token_type in UNARY_OPERATORS

def get_operator_precedence(token_type: TokenType) -> int:
    """Get operator precedence (higher number = higher precedence)"""
    return OPERATOR_PRECEDENCE.get(token_type, 0)

def is_right_associative(token_type: TokenType) -> bool:
    """Check if operator is right associative"""
    # In SimpleLang, all operators are left associative except unary operators
    return token_type in UNARY_OPERATORS

# Grammar production rules for reference
GRAMMAR_RULES = {
    'program': ['statement_list'],
    'statement_list': [
        'statement',
        'statement statement_list'
    ],
    'statement': [
        'declaration',
        'assignment', 
        'control_statement',
        'print_statement',
        'block'
    ],
    'declaration': [
        'type identifier ;',
        'type identifier = expression ;'  # Combined declaration and initialization
    ],
    'type': ['int', 'bool', 'string'],
    'print_statement': [
        'dikhao ( expression_list ) ;'
    ],
    'expression_list': [
        'expression',
        'expression , expression_list'
    ]
}

