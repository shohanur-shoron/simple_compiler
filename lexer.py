import ply.lex as lex


class Lexer:
    
    reserved = {
        'auto': 'AUTO', 'break': 'BREAK', 'case': 'CASE', 'char': 'CHAR',
        'const': 'CONST', 'continue': 'CONTINUE', 'default': 'DEFAULT',
        'do': 'DO', 'double': 'DOUBLE', 'else': 'ELSE', 'enum': 'ENUM',
        'extern': 'EXTERN', 'float': 'FLOAT', 'for': 'FOR', 'goto': 'GOTO',
        'if': 'IF', 'int': 'INT', 'long': 'LONG', 'register': 'REGISTER',
        'return': 'RETURN', 'short': 'SHORT', 'signed': 'SIGNED',
        'sizeof': 'SIZEOF', 'static': 'STATIC', 'struct': 'STRUCT',
        'switch': 'SWITCH', 'typedef': 'TYPEDEF', 'union': 'UNION',
        'unsigned': 'UNSIGNED', 'void': 'VOID', 'volatile': 'VOLATILE',
        'while': 'WHILE'
    }
    
    tokens = [
        'ID', 'CONSTANT', 'FLOAT_CONSTANT', 'STRING',
        'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MODULO',
        'ASSIGN', 'LT', 'LE', 'GT', 'GE', 'EQ', 'NE',
        'SEMICOLON', 'COMMA',
        'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'LBRACKET', 'RBRACKET'
    ] + list(reserved.values())
    
    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_TIMES = r'\*'
    t_DIVIDE = r'/'
    t_MODULO = r'%'
    t_ASSIGN = r'='
    t_LT = r'<'
    t_GT = r'>'
    t_LE = r'<='
    t_GE = r'>='
    t_EQ = r'=='
    t_NE = r'!='
    t_SEMICOLON = r';'
    t_COMMA = r','
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACE = r'\{'
    t_RBRACE = r'\}'
    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'
    t_ignore = ' \t'
    
    def t_STRING(self, t):
        r'"([^"\\]|\\.)*"'
        print(f"String: {t.value}")
        return t
    
    def t_FLOAT_CONSTANT(self, t):
        r'\d+\.\d+'
        t.value = float(t.value)
        print(f"Constant: {t.value}")
        return t
    
    def t_CONSTANT(self, t):
        r'\d+'
        t.value = int(t.value)
        print(f"Constant: {t.value}")
        return t
    
    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        t.type = self.reserved.get(t.value, 'ID')
        if t.type == 'ID':
            print(f"Identifier: {t.value}")
        else:
            print(f"Keyword: {t.value}")
        return t
    
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)
    
    def t_COMMENT_MULTI(self, t):
        r'/\*(.|\n)*?\*/'
        t.lexer.lineno += t.value.count('\n')
    
    def t_COMMENT_SINGLE(self, t):
        r'//.*'
        pass
    
    def t_error(self, t):
        print(f"Unrecognized character: {t.value[0]}")
        t.lexer.skip(1)
    
    def build(self):
        self.lexer = lex.lex(module=self)
        return self.lexer