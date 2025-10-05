class AssemblyGenerator:
    
    def __init__(self):
        self.assembly_code = []
        self.data_section = []
        self.register_map = {}
        self.available_registers = ['eax', 'ebx', 'ecx', 'edx', 'esi', 'edi']
        self.register_pool = self.available_registers.copy()
        self.stack_offset = 0
        self.variables = set()
        self.spill_index = 0

    def is_temporary(self, name):
        return name.startswith('t') and name[1:].isdigit()
    
    def get_register(self, temp):
        if temp in self.register_map:
            return self.register_map[temp]
        
        if self.register_pool:
            reg = self.register_pool.pop(0)
            self.register_map[temp] = reg
            print(f"Assembly: Allocating register {reg} for {temp}")
            return reg
        
        # Reuse a register. Simple strategy: pick the first one from the original list.
        reg_to_reuse = self.available_registers[self.spill_index]
        self.spill_index = (self.spill_index + 1) % len(self.available_registers)
        
        # Evict any temporary currently using this register
        for t, r in list(self.register_map.items()):
            if r == reg_to_reuse:
                del self.register_map[t]
                print(f"Assembly: Spilling {t} from {r} for {temp}")

        self.register_map[temp] = reg_to_reuse
        print(f"Assembly: Reusing register {reg_to_reuse} for {temp}")
        return reg_to_reuse
    
    def free_register(self, temp):
        if temp in self.register_map:
            reg = self.register_map[temp]
            print(f"Assembly: Freeing register {reg} from {temp}")
            if reg not in self.register_pool:
                self.register_pool.append(reg)
            del self.register_map[temp]
    
    def emit(self, instruction):
        self.assembly_code.append(f"    {instruction}")
    
    def emit_label(self, label):
        self.assembly_code.append(f"{label}:")
    
    def add_variable(self, var):
        if var not in self.variables:
            self.variables.add(var)
            self.data_section.append(f"{var} dd 0")
    
    def generate_from_tac(self, tac_code):
        print("\n" + "=" * 50)
        print("ASSEMBLY CODE GENERATION")
        print("=" * 50)
        
        lines = tac_code.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            print(f"Processing TAC: {line}")
            
            if '=' in line and not any(op in line for op in ['<', '>', '==', '!=', '<=', '>=']):
                self.handle_assignment(line)
            
            elif line.startswith('MOV'):
                self.handle_mov(line)
            
            elif line.startswith('IF'):
                self.handle_if(line)
            
            elif line.startswith('GOTO'):
                self.handle_goto(line)
            
            elif line.endswith(':'):
                label = line[:-1]
                print(f"Assembly: Label {label}")
                self.emit_label(label)
        
        return self.get_assembly_code()
    
    def handle_assignment(self, line):
        parts = line.split('=')
        dest = parts[0].strip()
        expr = parts[1].strip()

        op_map = {'+': 'add', '-': 'sub', '*': 'imul'}

        # Check for binary operations
        for op_char in op_map:
            if op_char in expr:
                op_instr = op_map[op_char]
                left, right = expr.split(op_char, 1)
                left = left.strip()
                right = right.strip()

                # Use left operand's register as the destination for the result
                if self.is_temporary(left):
                    dest_reg = self.get_register(left)
                else:
                    # If left is not a temp, get a new register for the destination
                    dest_reg = self.get_register(dest)
                    if left.isdigit():
                        self.emit(f"mov {dest_reg}, {left}")
                    else:
                        self.add_variable(left)
                        self.emit(f"mov {dest_reg}, [{left}]")
                
                # Perform operation with right operand
                if self.is_temporary(right):
                    right_reg = self.get_register(right)
                    self.emit(f"{op_instr} {dest_reg}, {right_reg}")
                    self.free_register(right)
                elif right.isdigit():
                    self.emit(f"{op_instr} {dest_reg}, {right}")
                else:
                    self.add_variable(right)
                    self.emit(f"{op_instr} {dest_reg}, [{right}]")

                # The result is in dest_reg. Update mapping for the destination temporary.
                if self.is_temporary(left) and dest != left:
                    self.register_map.pop(left, None)
                self.register_map[dest] = dest_reg
                return

        # Handle division and modulo
        if '/' in expr or '%' in expr:
            op = '/' if '/' in expr else '%'
            left, right = expr.split(op, 1)
            left = left.strip()
            right = right.strip()

            if self.is_temporary(left):
                left_reg = self.get_register(left)
                self.emit(f"mov eax, {left_reg}")
                self.free_register(left)
            elif left.isdigit():
                self.emit(f"mov eax, {left}")
            else:
                self.add_variable(left)
                self.emit(f"mov eax, [{left}]")
            
            self.emit("xor edx, edx")

            if self.is_temporary(right):
                right_reg = self.get_register(right)
                self.emit(f"idiv {right_reg}")
                self.free_register(right)
            elif right.isdigit():
                self.emit(f"mov ebx, {right}")
                self.emit(f"idiv ebx")
            else:
                self.add_variable(right)
                self.emit(f"idiv dword [{right}]")

            result_reg_name = 'eax' if op == '/' else 'edx'
            dest_reg = self.get_register(dest)
            if dest_reg != result_reg_name:
                self.emit(f"mov {dest_reg}, {result_reg_name}")
            return

        # Simple assignment
        else:
            value = expr.strip()
            dest_reg = self.get_register(dest)
            if self.is_temporary(value):
                src_reg = self.get_register(value)
                self.emit(f"mov {dest_reg}, {src_reg}")
                self.free_register(value)
            elif value.isdigit():
                self.emit(f"mov {dest_reg}, {value}")
            else:
                self.add_variable(value)
                self.emit(f"mov {dest_reg}, [{value}]")
    
    def handle_mov(self, line):
        parts = line.replace('MOV', '').strip().split(',')
        dest = parts[0].strip()
        src = parts[1].strip()
        
        self.add_variable(dest)
        
        if self.is_temporary(src):
            src_reg = self.get_register(src)
            print(f"Assembly: mov [{dest}], {src_reg}")
            self.emit(f"mov [{dest}], {src_reg}")
            self.free_register(src)
        elif src.isdigit():
            print(f"Assembly: mov [{dest}], {src}")
            self.emit(f"mov [{dest}], {src}")
        else:
            print(f"Assembly: mov eax, [{src}]")
            self.emit(f"mov eax, [{src}]")
            print(f"Assembly: mov [{dest}], eax")
            self.emit(f"mov [{dest}], eax")
            self.add_variable(src)
    
    def handle_if(self, line):
        parts = line.replace('IF', '').replace('GOTO', '').strip().split()
        left = parts[0]
        op = parts[1]
        right = parts[2]
        label = parts[3]
        
        if self.is_temporary(left):
            left_reg = self.get_register(left)
        else:
            left_reg = 'eax'
            print(f"Assembly: mov {left_reg}, [{left}]")
            self.emit(f"mov {left_reg}, [{left}]")
            self.add_variable(left)
        
        if self.is_temporary(right):
            right_reg = self.get_register(right)
            print(f"Assembly: cmp {left_reg}, {right_reg}")
            self.emit(f"cmp {left_reg}, {right_reg}")
        elif right.isdigit():
            print(f"Assembly: cmp {left_reg}, {right}")
            self.emit(f"cmp {left_reg}, {right}")
        else:
            print(f"Assembly: cmp {left_reg}, [{right}]")
            self.emit(f"cmp {left_reg}, [{right}]")
            self.add_variable(right)
        
        jump_map = {
            '<': 'jl',
            '<=': 'jle',
            '>': 'jg',
            '>=': 'jge',
            '==': 'je',
            '!=': 'jne'
        }
        
        jump_instr = jump_map.get(op, 'jmp')
        print(f"Assembly: {jump_instr} {label}")
        self.emit(f"{jump_instr} {label}")
    
    def handle_goto(self, line):
        label = line.replace('GOTO', '').strip()
        print(f"Assembly: jmp {label}")
        self.emit(f"jmp {label}")
    
    def get_assembly_code(self):
        full_code = []
        full_code.append("section .data")
        full_code.extend(self.data_section)
        full_code.append("")
        full_code.append("section .text")
        full_code.append("    global _start")
        full_code.append("")
        full_code.append("_start:")
        full_code.extend(self.assembly_code)
        full_code.append("")
        full_code.append("    ; Exit program")
        full_code.append("    mov eax, 1")
        full_code.append("    xor ebx, ebx")
        full_code.append("    int 0x80")
        
        return '\n'.join(full_code)
