class CodeGen:
    
    def __init__(self):
        self.temp_count = 0
        self.label_count = 0
        self.code = []
    
    def new_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"
    
    def new_label(self):
        self.label_count += 1
        return f"L{self.label_count}"
    
    def emit(self, instruction):
        self.code.append(instruction)
    
    def get_code(self):
        return '\n'.join(self.code)
    
    def reset(self):
        self.temp_count = 0
        self.label_count = 0
        self.code = []