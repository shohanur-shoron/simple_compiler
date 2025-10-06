from lexer import Lexer
from codegen import CodeGen
from parser import Parser, SyntaxErrorFound
from assembly_gen import AssemblyGenerator
from semantic import SemanticAnalyzer, SemanticError


class Compiler:
    
    def __init__(self):
        self.lexer = Lexer().build()
        self.codegen = CodeGen()
        self.parser = Parser(self.codegen).build()
        self.asm_gen = AssemblyGenerator()
        self.semantic_analyzer = SemanticAnalyzer(self.codegen)
    
    def tokenize(self, text):
        print("=" * 50)
        print("TOKENIZATION")
        print("=" * 50)
        self.lexer.input(text)
        
        for tok in self.lexer:
            if tok.type in ['PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MODULO']:
                print(f"Arithmetic Operator: {tok.value}")
            elif tok.type in ['SEMICOLON', 'COMMA']:
                print(f"Punctuation: {tok.value}")
            elif tok.type in ['LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'LBRACKET', 'RBRACKET']:
                print(f"Parenthesis: {tok.value}")
            elif tok.type in ['ASSIGN', 'LT', 'LE', 'GT', 'GE', 'EQ', 'NE']:
                print(f"Relational/Assignment Operator: {tok.value}")
        print()
    
    def compile(self, text):
        self.codegen.reset()
        self.semantic_analyzer.reset()
        self.tokenize(text)
        
        print("=" * 50)
        print("PARSING AND SEMANTIC ANALYSIS")
        print("=" * 50)
        
        self.lexer.lineno = 1
        try:
            ast = self.parser.parse(text, lexer=self.lexer)
            self.semantic_analyzer.analyze(ast)
        except SyntaxErrorFound:
            print("\n" + "=" * 50)
            print("COMPILATION FAILED DUE TO SYNTAX ERROR.")
            print("=" * 50 + "\n")
            return
        except Exception as e:
            print("\n" + "=" * 50)
            print(f"COMPILATION FAILED DUE TO SEMANTIC ERROR: {e}")
            print("=" * 50 + "\n")
            return
        
        print("\n" + "=" * 50)
        print("GENERATED INTERMEDIATE CODE (TAC)")
        print("=" * 50)
        tac_code = self.codegen.get_code()
        print(tac_code)
        print()
        
        self.asm_gen = AssemblyGenerator()
        asm_code = self.asm_gen.generate_from_tac(tac_code)
        
        print("\n" + "=" * 50)
        print("GENERATED ASSEMBLY CODE (x86)")
        print("=" * 50)
        print(asm_code)
        print()
