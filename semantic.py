class SemanticError(Exception):
    pass

class Symbol:
    def __init__(self, name, type):
        self.name = name
        self.type = type

class SymbolTable:
    def __init__(self):
        self.scopes = [{}]

    def enter_scope(self):
        print("Semantic: Entering new scope")
        self.scopes.append({})

    def exit_scope(self):
        print("Semantic: Exiting scope")
        self.scopes.pop()

    def add_symbol(self, symbol):
        print(f"Semantic: Adding symbol '{symbol.name}' of type '{symbol.type}'")
        if symbol.name in self.scopes[-1]:
            raise SemanticError(f"Variable '{symbol.name}' already declared in this scope.")
        self.scopes[-1][symbol.name] = symbol

    def lookup_symbol(self, name):
        print(f"Semantic: Looking up symbol '{name}'")
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

class SemanticAnalyzer:
    def __init__(self, codegen):
        self.symbol_table = SymbolTable()
        self.codegen = codegen

    def reset(self):
        self.symbol_table = SymbolTable()

    def analyze(self, node):
        if node is None:
            return
        if isinstance(node, list):
            for item in node:
                self.analyze(item)
            return

        method_name = 'analyze_' + node[0]
        method = getattr(self, method_name, self.default_analyzer)
        return method(node)

    def default_analyzer(self, node):
        if isinstance(node, list):
            for item in node:
                self.analyze(item)
        elif isinstance(node, tuple):
            for item in node[1:]:
                if isinstance(item, (tuple, list)):
                    self.analyze(item)

    def analyze_program(self, node):
        print("Semantic: Analyzing program")
        self.analyze(node[1])
        self.generate_tac(node)

    def analyze_statement_list(self, node):
        print("Semantic: Analyzing statement list")
        for statement in node:
            self.analyze(statement)

    def analyze_declaration(self, node):
        print(f"Semantic: Analyzing declaration for '{node[2]}'")
        symbol = Symbol(node[2], node[1])
        self.symbol_table.add_symbol(symbol)

    def analyze_declaration_assign(self, node):
        print(f"Semantic: Analyzing declaration with assignment for '{node[2]}'")
        symbol = Symbol(node[2], node[1])
        self.symbol_table.add_symbol(symbol)
        self.analyze(node[3])

    def analyze_assign(self, node):
        print(f"Semantic: Analyzing assignment to '{node[1]}'")
        if not self.symbol_table.lookup_symbol(node[1]):
            raise SemanticError(f"Undeclared variable '{node[1]}' used in assignment.")
        self.analyze(node[2])

    def analyze_increment(self, node):
        print(f"Semantic: Analyzing increment for '{node[1]}'")
        if not self.symbol_table.lookup_symbol(node[1]):
            raise SemanticError(f"Undeclared variable '{node[1]}' used in increment.")

    def analyze_decrement(self, node):
        print(f"Semantic: Analyzing decrement for '{node[1]}'")
        if not self.symbol_table.lookup_symbol(node[1]):
            raise SemanticError(f"Undeclared variable '{node[1]}' used in decrement.")

    def analyze_id(self, node):
        print(f"Semantic: Analyzing ID '{node[1]}'")
        if not self.symbol_table.lookup_symbol(node[1]):
            raise SemanticError(f"Undeclared variable '{node[1]}' used in expression.")

    def analyze_if(self, node):
        print("Semantic: Analyzing if statement")
        self.analyze(node[1])
        self.analyze(node[2])

    def analyze_if_else(self, node):
        print("Semantic: Analyzing if-else statement")
        self.analyze(node[1])
        self.analyze(node[2])
        self.analyze(node[3])

    def analyze_for(self, node):
        print("Semantic: Analyzing for loop")
        self.symbol_table.enter_scope()
        self.analyze(node[1])
        self.analyze(node[2])
        self.analyze(node[3])
        self.analyze(node[4])
        self.symbol_table.exit_scope()

    def analyze_block(self, node):
        print("Semantic: Analyzing block")
        self.symbol_table.enter_scope()
        self.analyze(node[1])
        self.symbol_table.exit_scope()
        
    def analyze_binop(self, node):
        print(f"Semantic: Analyzing binary operation '{node[1]}'")
        self.analyze(node[2])
        self.analyze(node[3])

    def analyze_uminus(self, node):
        print("Semantic: Analyzing unary minus")
        self.analyze(node[1])

    def analyze_condition(self, node):
        print(f"Semantic: Analyzing condition '{node[1]}'")
        self.analyze(node[2])
        self.analyze(node[3])

    def generate_tac(self, node):
        if isinstance(node, list):
            for item in node:
                self.generate_tac(item)
            return

        method_name = 'generate_tac_' + node[0]
        method = getattr(self, method_name, self.default_generate_tac)
        return method(node)

    def default_generate_tac(self, node):
        if isinstance(node, list):
            for item in node:
                self.generate_tac(item)
        elif isinstance(node, tuple):
            for item in node[1:]:
                if isinstance(item, (tuple, list)):
                    self.generate_tac(item)

    def generate_tac_program(self, node):
        self.generate_tac(node[1])

    def generate_tac_statement_list(self, node):
        for statement in node:
            self.generate_tac(statement)

    def generate_tac_assign(self, stmt):
        expr_temp = self.generate_tac_expression(stmt[2])
        self.codegen.emit(f"MOV {stmt[1]}, {expr_temp}")

    def generate_tac_increment(self, stmt):
        self.codegen.emit(f"ADD {stmt[1]}, {stmt[1]}, 1")

    def generate_tac_decrement(self, stmt):
        self.codegen.emit(f"SUB {stmt[1]}, {stmt[1]}, 1")

    def generate_tac_if(self, stmt):
        cond_result = self.generate_tac_condition(stmt[1])
        label_true = self.codegen.new_label()
        label_end = self.codegen.new_label()
        
        self.codegen.emit(f"IF {cond_result[0]} {cond_result[1]} {cond_result[2]} GOTO {label_true}")
        self.codegen.emit(f"GOTO {label_end}")
        self.codegen.emit(f"{label_true}:")
        
        self.generate_tac(stmt[2])
        
        self.codegen.emit(f"{label_end}:")

    def generate_tac_if_else(self, stmt):
        cond_result = self.generate_tac_condition(stmt[1])
        label_true = self.codegen.new_label()
        label_false = self.codegen.new_label()
        label_end = self.codegen.new_label()
        
        self.codegen.emit(f"IF {cond_result[0]} {cond_result[1]} {cond_result[2]} GOTO {label_true}")
        self.codegen.emit(f"GOTO {label_false}")
        self.codegen.emit(f"{label_true}:")
        
        self.generate_tac(stmt[2])
        
        self.codegen.emit(f"GOTO {label_end}")
        self.codegen.emit(f"{label_false}:")
        
        self.generate_tac(stmt[3])
        
        self.codegen.emit(f"{label_end}:")

    def generate_tac_for(self, stmt):
        init_stmt = stmt[1]
        condition = stmt[2]
        increment = stmt[3]
        body = stmt[4]
        
        self.generate_tac(init_stmt)
        
        label_start = self.codegen.new_label()
        label_body = self.codegen.new_label()
        label_end = self.codegen.new_label()
        
        self.codegen.emit(f"{label_start}:")
        
        cond_result = self.generate_tac_condition(condition)
        self.codegen.emit(f"IF {cond_result[0]} {cond_result[1]} {cond_result[2]} GOTO {label_body}")
        self.codegen.emit(f"GOTO {label_end}")
        
        self.codegen.emit(f"{label_body}:")
        
        self.generate_tac(body)
        
        self.generate_tac(increment)
        
        self.codegen.emit(f"GOTO {label_start}")
        self.codegen.emit(f"{label_end}:")

    def generate_tac_block(self, node):
        for s in node[1]:
            self.generate_tac(s)

    def generate_tac_declaration(self, node):
        pass

    def generate_tac_declaration_assign(self, stmt):
        expr_temp = self.generate_tac_expression(stmt[3])
        self.codegen.emit(f"MOV {stmt[2]}, {expr_temp}")

    def generate_tac_expression(self, expr):
        if expr[0] == 'const':
            temp = self.codegen.new_temp()
            self.codegen.emit(f"{temp} = {expr[1]}")
            return temp
        elif expr[0] == 'id':
            temp = self.codegen.new_temp()
            self.codegen.emit(f"{temp} = {expr[1]}")
            return temp
        elif expr[0] == 'binop':
            left = self.generate_tac_expression(expr[2])
            right = self.generate_tac_expression(expr[3])
            temp = self.codegen.new_temp()
            self.codegen.emit(f"{temp} = {left} {expr[1]} {right}")
            return temp
        elif expr[0] == 'uminus':
            expr_temp = self.generate_tac_expression(expr[1])
            temp = self.codegen.new_temp()
            self.codegen.emit(f"{temp} = 0 - {expr_temp}")
            return temp
        return None

    def generate_tac_condition(self, cond):
        left = self.generate_tac_expression(cond[2])
        right = self.generate_tac_expression(cond[3])
        return (left, cond[1], right)
