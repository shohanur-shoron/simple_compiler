import ply.yacc as yacc
from lexer import Lexer

class SyntaxErrorFound(Exception):
    pass


class Parser:
    
    def __init__(self, codegen):
        self.codegen = codegen
        self.tokens = Lexer.tokens
        self.precedence = (
            ('left', 'PLUS', 'MINUS'),
            ('left', 'TIMES', 'DIVIDE', 'MODULO'),
            ('right', 'UMINUS'),
        )
    
    def p_program(self, p):
        'program : statement_list'
        print("Parsing: program -> statement_list")
        p[0] = ('program', p[1])
    
    def p_statement_list(self, p):
        '''statement_list : statement_list statement
                         | statement'''
        if len(p) == 3:
            print("Parsing: statement_list -> statement_list statement")
            p[0] = p[1] + [p[2]]
        else:
            print("Parsing: statement_list -> statement")
            p[0] = [p[1]]
    
    def p_statement(self, p):
        '''statement : assignment
                    | if_statement
                    | for_statement
                    | block
                    | declaration
                    | increment_statement
                    | decrement_statement'''
        stmt_type = p[1][0] if isinstance(p[1], tuple) else 'unknown'
        print(f"Parsing: statement -> {stmt_type}")
        p[0] = p[1]

    def p_increment_statement(self, p):
        'increment_statement : ID INCREMENT SEMICOLON'
        p[0] = ('increment', p[1])

    def p_decrement_statement(self, p):
        'decrement_statement : ID DECREMENT SEMICOLON'
        p[0] = ('decrement', p[1])
    
    def p_declaration(self, p):
        '''declaration : INT ID SEMICOLON
                      | FLOAT ID SEMICOLON
                      | CHAR ID SEMICOLON
                      | DOUBLE ID SEMICOLON
                      | VOID ID SEMICOLON
                      | INT ID ASSIGN expression SEMICOLON
                      | FLOAT ID ASSIGN expression SEMICOLON
                      | CHAR ID ASSIGN expression SEMICOLON
                      | DOUBLE ID ASSIGN expression SEMICOLON'''
        if len(p) == 6:
            print(f"Parsing: declaration -> {p[1]} {p[2]} = expression")
            p[0] = ('declaration_assign', p[1], p[2], p[4])
        elif len(p) == 4:
            print(f"Parsing: declaration -> {p[1]} {p[2]}")
            p[0] = ('declaration', p[1], p[2])

    def p_assignment(self, p):
        'assignment : ID ASSIGN expression SEMICOLON'
        print(f"Parsing: assignment -> {p[1]} = expression")
        p[0] = ('assign', p[1], p[3])

    def p_if_statement(self, p):
        '''if_statement : IF LPAREN condition RPAREN statement
                       | IF LPAREN condition RPAREN statement ELSE statement'''
        if len(p) == 8:
            print("Parsing: if_statement -> if (condition) statement else statement")
            p[0] = ('if_else', p[3], p[5], p[7])
        else:
            print("Parsing: if_statement -> if (condition) statement")
            p[0] = ('if', p[3], p[5])

    def p_for_statement(self, p):
        'for_statement : FOR LPAREN for_init SEMICOLON condition SEMICOLON for_increment RPAREN statement'
        print("Parsing: for_statement -> for (for_init; condition; increment) statement")
        p[0] = ('for', p[3], p[5], p[7], p[9])

    def p_for_init(self, p):
        """for_init : assignment_no_semicolon
                    | empty"""
        p[0] = p[1]

    def p_assignment_no_semicolon(self, p):
        'assignment_no_semicolon : ID ASSIGN expression'
        print(f"Parsing: assignment_no_semicolon -> {p[1]} = expression")
        p[0] = ('assign', p[1], p[3])

    def p_empty(self, p):
        'empty :'
        p[0] = None

    def p_for_increment(self, p):
        '''for_increment : ID ASSIGN expression
                         | ID INCREMENT
                         | ID DECREMENT'''
        if len(p) == 4:
            p[0] = ('assign', p[1], p[3])
        else:
            if p[2] == '++':
                p[0] = ('increment', p[1])
            else:
                p[0] = ('decrement', p[1])
    
    def p_block(self, p):
        'block : LBRACE statement_list RBRACE'
        print("Parsing: block -> { statement_list }")
        p[0] = ('block', p[2])
    
    def p_expression_binop(self, p):
        '''expression : expression PLUS expression
                     | expression MINUS expression
                     | expression TIMES expression
                     | expression DIVIDE expression
                     | expression MODULO expression'''
        print(f"Parsing: expression -> expression {p[2]} expression")
        p[0] = ('binop', p[2], p[1], p[3])

    def p_expression_uminus(self, p):
        'expression : MINUS expression %prec UMINUS'
        print("Parsing: expression -> - expression")
        p[0] = ('uminus', p[2])
    
    def p_expression_id(self, p):
        'expression : ID'
        print(f"Parsing: expression -> ID ({p[1]})")
        p[0] = ('id', p[1])
    
    def p_expression_constant(self, p):
        '''expression : CONSTANT
                     | FLOAT_CONSTANT'''
        print(f"Parsing: expression -> CONSTANT ({p[1]})")
        p[0] = ('const', p[1])
    
    def p_expression_paren(self, p):
        'expression : LPAREN expression RPAREN'
        print("Parsing: expression -> ( expression )")
        p[0] = p[2]
    
    def p_condition(self, p):
        '''condition : expression LT expression
                    | expression LE expression
                    | expression GT expression
                    | expression GE expression
                    | expression EQ expression
                    | expression NE expression'''
        print(f"Parsing: condition -> expression {p[2]} expression")
        p[0] = ('condition', p[2], p[1], p[3])
    
    def p_error(self, p):
        if p:
            message = f"Syntax error at token {p.type} ('{p.value}') on line {p.lineno}"
            print(message)
            raise SyntaxErrorFound(message)
        else:
            message = "Syntax error at EOF"
            print(message)
            raise SyntaxErrorFound(message)
    
    def build(self):
        self.parser = yacc.yacc(module=self)
        return self.parser