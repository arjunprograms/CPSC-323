import sys
import re
import os  # Added import for file path manipulations

# Token types
KEYWORDS = {'integer', 'while', 'if', 'fi', 'put', 'get'}
OPERATORS = {'+', '-', '*', '/', '==', '!=', '>', '<', '>=', '<=', '=', '(', ')', '{', '}', ';', ',', '<=', '>=', '==', '!='}

# Token class
class Token:
    def __init__(self, type_, value, line):
        self.type = type_
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Token({self.type}, {self.value}, Line {self.line})"

# Lexer class
class Lexer:
    def __init__(self, text):
        self.text = text
        self.tokens = []
        self.current_pos = 0
        self.line = 1

    def tokenize(self):
        token_specification = [
            ('NUMBER',   r'\d+'),
            ('ID',       r'[A-Za-z_]\w*'),
            ('OP',       r'==|!=|>=|<=|[+\-*/><=]'),
            ('LPAREN',   r'\('),
            ('RPAREN',   r'\)'),
            ('LBRACE',   r'\{'),
            ('RBRACE',   r'\}'),
            ('SEMICOLON',r';'),
            ('COMMA',    r','),
            ('SKIP',     r'[ \t]+'),
            ('NEWLINE',  r'\n'),
            ('MISMATCH', r'.'),  # Any other character
        ]
        tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
        get_token = re.compile(tok_regex).match
        mo = get_token(self.text)
        while mo is not None:
            kind = mo.lastgroup
            value = mo.group()
            if kind == 'NUMBER':
                token = Token('INT', int(value), self.line)
                self.tokens.append(token)
            elif kind == 'ID':
                if value in KEYWORDS:
                    token = Token('KEYWORD', value, self.line)
                else:
                    token = Token('ID', value, self.line)
                self.tokens.append(token)
            elif kind == 'OP':
                token = Token('OPERATOR', value, self.line)
                self.tokens.append(token)
            elif kind == 'LPAREN':
                token = Token('LPAREN', value, self.line)
                self.tokens.append(token)
            elif kind == 'RPAREN':
                token = Token('RPAREN', value, self.line)
                self.tokens.append(token)
            elif kind == 'LBRACE':
                token = Token('LBRACE', value, self.line)
                self.tokens.append(token)
            elif kind == 'RBRACE':
                token = Token('RBRACE', value, self.line)
                self.tokens.append(token)
            elif kind == 'SEMICOLON':
                token = Token('SEMICOLON', value, self.line)
                self.tokens.append(token)
            elif kind == 'COMMA':
                token = Token('COMMA', value, self.line)
                self.tokens.append(token)
            elif kind == 'NEWLINE':
                self.line += 1
            elif kind == 'SKIP':
                pass
            elif kind == 'MISMATCH':
                raise RuntimeError(f'Unexpected character {value!r} on line {self.line}')
            self.current_pos = mo.end()
            mo = get_token(self.text, self.current_pos)
        self.tokens.append(Token('EOF', '', self.line))
        return self.tokens

# Parser class
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0
        self.current_token = self.tokens[self.current_token_index]
        self.symbol_table = {}
        self.memory_location = 9000
        self.assembly = []
        self.address = 1
        self.label_count = 0

    def error(self, message):
        raise Exception(f'Error on line {self.current_token.line}: {message}')

    def advance(self):
        self.current_token_index += 1
        if self.current_token_index < len(self.tokens):
            self.current_token = self.tokens[self.current_token_index]
        else:
            self.current_token = Token('EOF', '', self.current_token.line)

    def peek(self):
        peek_index = self.current_token_index + 1
        if peek_index < len(self.tokens):
            return self.tokens[peek_index]
        else:
            return Token('EOF', '', self.current_token.line)

    def consume(self, token_type, value=None):
        if self.current_token.type == token_type and (value is None or self.current_token.value == value):
            self.advance()
        else:
            expected = value if value else token_type
            self.error(f'Expected {expected}, got {self.current_token.value}')

    def parse(self):
        while self.current_token.type != 'EOF':
            if self.current_token.type == 'KEYWORD' and self.current_token.value == 'integer':
                self.declaration()
            elif self.current_token.type == 'ID':
                self.assignment()
            elif self.current_token.type == 'KEYWORD' and self.current_token.value == 'while':
                self.while_loop()
            elif self.current_token.type == 'KEYWORD' and self.current_token.value == 'if':
                self.if_statement()
            elif self.current_token.type == 'KEYWORD' and self.current_token.value in {'put', 'get'}:
                self.io_statement()
            else:
                self.error(f'Unexpected token {self.current_token.value}')

    def declaration(self):
        print(f"DEBUG: Parsing token: ({self.current_token.type}, '{self.current_token.value}')")
        print(f"DEBUG: Starting declaration with token: ({self.current_token.type}, '{self.current_token.value}')")
        self.consume('KEYWORD', 'integer')
        while True:
            if self.current_token.type != 'ID':
                self.error('Expected identifier in declaration')
            var_name = self.current_token.value
            print(f"DEBUG: Declared variable: {var_name}")
            if var_name in self.symbol_table:
                self.error(f'Variable {var_name} already declared')
            self.symbol_table[var_name] = self.memory_location
            self.memory_location += 1
            self.advance()
            if self.current_token.type == 'COMMA':
                self.advance()
                continue
            elif self.current_token.type == 'SEMICOLON':
                self.advance()
                break
            else:
                self.error('Expected comma or semicolon in declaration')

    def assignment(self):
        var_name = self.current_token.value
        print(f"DEBUG: Parsing token: ({self.current_token.type}, '{self.current_token.value}')")
        print(f"DEBUG: Entering assignment with token: ({self.current_token.type}, '{self.current_token.value}')")
        if var_name not in self.symbol_table:
            self.error(f'Variable {var_name} not declared')
        self.advance()
        self.consume('OPERATOR', '=')
        self.expression()
        self.consume('SEMICOLON')
        # Assign the result to the variable
        self.assembly.append({'address': self.address, 'operation': 'POPM', 'operand': self.symbol_table[var_name]})
        print(f"DEBUG: Assigned {var_name} to memory location {self.symbol_table[var_name]}")
        self.address += 1

    def while_loop(self):
        print(f"DEBUG: Parsing token: (KEYWORD, '{self.current_token.value}')")
        print(f"DEBUG: Entering while statement with token: (KEYWORD, '{self.current_token.value}')")
        self.consume('KEYWORD', 'while')
        self.consume('LPAREN')
        # Save current address for the loop start
        loop_start = self.address
        self.assembly.append({'address': self.address, 'operation': 'LABEL', 'operand': ''})
        print(f"DEBUG: LABEL inserted at address {self.address}")
        self.address += 1
        # Parse condition
        self.expression()
        # After condition, perform the jump if false
        jump_if_false_address = self.address
        self.assembly.append({'address': self.address, 'operation': 'JUMPZ', 'operand': 'placeholder'})
        print(f"DEBUG: Back-patching jump at address {self.address} to target address after loop")
        self.address += 1
        # Parse loop body
        self.consume('RPAREN')
        self.consume('LBRACE')
        while not (self.current_token.type == 'RBRACE'):
            if self.current_token.type == 'ID':
                self.assignment()
            elif self.current_token.type == 'KEYWORD' and self.current_token.value in {'put', 'get'}:
                self.io_statement()
            elif self.current_token.type == 'KEYWORD' and self.current_token.value == 'while':
                self.while_loop()
            elif self.current_token.type == 'KEYWORD' and self.current_token.value == 'if':
                self.if_statement()
            else:
                self.error(f'Unexpected token {self.current_token.value} in while loop')
        self.consume('RBRACE')
        # After loop body, jump back to loop start
        self.assembly.append({'address': self.address, 'operation': 'JUMP', 'operand': loop_start})
        print(f"DEBUG: JUMP to address {loop_start} from address {self.address}")
        self.address += 1
        # Insert a NOP (No Operation) to mark loop end
        self.assembly.append({'address': self.address, 'operation': 'NOP', 'operand': ''})
        print(f"DEBUG: NOP inserted at address {self.address} for loop end")
        loop_end = self.address
        # Back-patch the JUMPZ to point to the loop end
        self.assembly[jump_if_false_address -1]['operand'] = loop_end
        print(f"DEBUG: Back-patched jump at address {jump_if_false_address} to target address {loop_end}")
        self.address +=1

    def if_statement(self):
        print(f"DEBUG: Parsing token: (KEYWORD, '{self.current_token.value}')")
        print(f"DEBUG: Entering if statement with token: (KEYWORD, '{self.current_token.value}')")
        self.consume('KEYWORD', 'if')
        self.consume('LPAREN')
        # Parse condition
        self.expression()
        # After condition, perform the jump if false
        jump_if_false_address = self.address
        self.assembly.append({'address': self.address, 'operation': 'JUMPZ', 'operand': 'placeholder'})
        print(f"DEBUG: Back-patching jump at address {self.address} to target address after if")
        self.address += 1
        self.consume('RPAREN')
        self.consume('LBRACE')
        # Parse if body
        while not (self.current_token.type == 'RBRACE'):
            if self.current_token.type == 'ID':
                self.assignment()
            elif self.current_token.type == 'KEYWORD' and self.current_token.value in {'put', 'get'}:
                self.io_statement()
            elif self.current_token.type == 'KEYWORD' and self.current_token.value == 'if':
                self.if_statement()
            else:
                self.error(f'Unexpected token {self.current_token.value} in if statement')
        self.consume('RBRACE')
        # Consume 'fi' token
        self.consume('KEYWORD', 'fi')
        # Set the jump_if_false to current address (after if)
        if_end = self.address
        self.assembly[jump_if_false_address -1]['operand'] = if_end
        print(f"DEBUG: Back-patched jump at address {jump_if_false_address} to target address {if_end}")
        # Insert NOP at if_end
        self.assembly.append({'address': self.address, 'operation': 'NOP', 'operand': ''})
        print(f"DEBUG: NOP inserted at address {self.address} for if end")
        self.address +=1

    def io_statement(self):
        stmt = self.current_token.value
        print(f"DEBUG: Parsing token: ({self.current_token.type}, '{self.current_token.value}')")
        print(f"DEBUG: Entering {stmt} statement with token: ({self.current_token.type}, '{self.current_token.value}')")
        self.advance()
        self.consume('LPAREN')
        if stmt == 'put':
            self.expression()
            self.consume('RPAREN')
            self.consume('SEMICOLON')
            # After expression, perform STDOUT
            self.assembly.append({'address': self.address, 'operation': 'STDOUT', 'operand': ''})
            print(f"DEBUG: Performed STDOUT operation")
            self.address += 1
        elif stmt == 'get':
            # For get, we assume STDIN followed by POPM to store in variable
            if self.current_token.type != 'ID':
                self.error('Expected identifier after get')
            var_name = self.current_token.value
            print(f"DEBUG: Parsing token inside {stmt}: (ID, '{self.current_token.value}')")
            if var_name not in self.symbol_table:
                self.error(f'Variable {var_name} not declared')
            self.advance()
            self.consume('RPAREN')
            self.consume('SEMICOLON')
            # Perform STDIN and store in variable
            self.assembly.append({'address': self.address, 'operation': 'STDIN', 'operand': ''})
            self.address +=1
            self.assembly.append({'address': self.address, 'operation': 'POPM', 'operand': self.symbol_table[var_name]})
            print(f"DEBUG: Performed STDIN and stored input in '{var_name}' at memory location {self.symbol_table[var_name]}")
            self.address +=1
        else:
            self.error(f'Unknown IO statement {stmt}')

    def expression(self):
        return self.logical_expression()

    def logical_expression(self):
        node = self.arith_expression()
        while self.current_token.type == 'OPERATOR' and self.current_token.value in {'==', '!=', '>', '<', '>=', '<='}:
            op = self.current_token.value
            print(f"DEBUG: Encountered '{op}' operator")
            self.advance()
            right = self.arith_expression()
            # At this point, both operands have been pushed onto the stack
            # Now, perform the operation
            self.assembly.append({'address': self.address, 'operation': self.operator_to_operation(op), 'operand': ''})
            print(f"DEBUG: Performed {self.operator_to_operation(op)} operation")
            self.address +=1
        return node

    def arith_expression(self):
        node = self.term()
        while self.current_token.type == 'OPERATOR' and self.current_token.value in {'+', '-'}:
            op = self.current_token.value
            print(f"DEBUG: Encountered '{op}' operator")
            self.advance()
            right = self.term()
            self.assembly.append({'address': self.address, 'operation': self.operator_to_operation(op), 'operand': ''})
            print(f"DEBUG: Performed {self.operator_to_operation(op)} operation")
            self.address +=1
        return node

    def term(self):
        node = self.factor()
        while self.current_token.type == 'OPERATOR' and self.current_token.value in {'*', '/'}:
            op = self.current_token.value
            print(f"DEBUG: Encountered '{op}' operator")
            self.advance()
            right = self.factor()
            self.assembly.append({'address': self.address, 'operation': self.operator_to_operation(op), 'operand': ''})
            print(f"DEBUG: Performed {self.operator_to_operation(op)} operation")
            self.address +=1
        return node

    def factor(self):
        token = self.current_token
        if token.type == 'INT':
            print(f"DEBUG: Pushed integer {token.value} onto stack")
            self.assembly.append({'address': self.address, 'operation': 'PUSHI', 'operand': token.value})
            self.address +=1
            self.advance()
            return token.value
        elif token.type == 'ID':
            var_name = token.value
            print(f"DEBUG: Pushed value of '{var_name}' from memory location {self.symbol_table[var_name]} onto stack")
            self.assembly.append({'address': self.address, 'operation': 'PUSHM', 'operand': self.symbol_table[var_name]})
            self.address +=1
            self.advance()
            return self.symbol_table[var_name]
        elif token.type == 'LPAREN':
            print(f"DEBUG: Encountered '(' indicating start of parenthesized expression")
            self.advance()
            node = self.expression()
            self.consume('RPAREN')
            print(f"DEBUG: Encountered ')' indicating end of parenthesized expression")
            return node
        else:
            self.error('Expected integer, identifier, or parenthesized expression')

    def operator_to_operation(self, op):
        mapping = {
            '+': 'ADD',
            '-': 'SUB',
            '*': 'MUL',
            '/': 'DIV',
            '==': 'EQ',
            '!=': 'NEQ',
            '>': 'GTR',
            '<': 'LSS',
            '>=': 'GEQ',
            '<=': 'LEQ',
        }
        return mapping.get(op, 'UNKNOWN')

    def generate_assembly(self):
        # This function already populates self.assembly during parsing
        pass

    def output_results(self, output_file):
        with open(output_file, 'w') as f:
            # Symbol Table
            f.write("Symbol Table:\n")
            f.write("{:<15} {:<20} {:<10}\n".format("Identifier", "MemoryLocation", "Type"))
            for var, loc in self.symbol_table.items():
                f.write("{:<15} {:<20} {:<10}\n".format(var, loc, "integer"))
            f.write("\nAssembly Code:\n")
            f.write("{:<10} {:<15} {:<10}\n".format("Address", "Operation", "Operand"))
            for instr in self.assembly:
                addr = instr['address']
                op = instr['operation']
                operand = instr['operand']
                if op == 'LABEL':
                    f.write("{:<10} {:<15} {}\n".format(addr, op, ''))
                elif op in {'JUMPZ', 'JUMP'} and isinstance(operand, int):
                    f.write("{:<10} {:<15} {}\n".format(addr, op, operand))
                elif op in {'JUMPZ', 'JUMP'} and operand == 'placeholder':
                    f.write("{:<10} {:<15} {}\n".format(addr, op, ''))
                elif operand != '':
                    f.write("{:<10} {:<15} {}\n".format(addr, op, operand))
                else:
                    f.write("{:<10} {:<15} {}\n".format(addr, op, ''))
            f.write("\n")
        print(f"Symbol Table:")
        print("{:<15} {:<20} {:<10}".format("Identifier", "MemoryLocation", "Type"))
        for var, loc in self.symbol_table.items():
            print("{:<15} {:<20} {:<10}".format(var, loc, "integer"))
        print("\nAssembly Code:")
        print("{:<10} {:<15} {:<10}".format("Address", "Operation", "Operand"))
        for instr in self.assembly:
            addr = instr['address']
            op = instr['operation']
            operand = instr['operand']
            if op == 'LABEL':
                print("{:<10} {:<15} {}".format(addr, op, ''))
            elif op in {'JUMPZ', 'JUMP'} and isinstance(operand, int):
                print("{:<10} {:<15} {}".format(addr, op, operand))
            elif op in {'JUMPZ', 'JUMP'} and operand == 'placeholder':
                print("{:<10} {:<15} {}".format(addr, op, ''))
            elif operand != '':
                print("{:<10} {:<15} {}".format(addr, op, operand))
            else:
                print("{:<10} {:<15} {}".format(addr, op, ''))
        print(f"\nOutput has been written to '{output_file}' in the directory '.'.")

# Main function
def main():
    if len(sys.argv) != 2:
        print("Usage: python rat24f_parser.py <source_file>")
        sys.exit(1)
    source_file = sys.argv[1]
    try:
        with open(source_file, 'r') as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: File '{source_file}' not found.")
        sys.exit(1)
    
    # Lexical Analysis
    lexer = Lexer(text)
    try:
        tokens = lexer.tokenize()
    except RuntimeError as e:
        print(e)
        sys.exit(1)
    
    # Parsing
    parser = Parser(tokens)
    try:
        parser.parse()
    except Exception as e:
        print(e)
        sys.exit(1)
    
    # Generate Assembly (already done during parsing)
    parser.generate_assembly()
    
    # Output Results
    # Updated output_file assignment to avoid double underscores
    output_file = f"output_{os.path.splitext(os.path.basename(source_file))[0]}.txt"
    parser.output_results(output_file)

if __name__ == '__main__':
    main()
