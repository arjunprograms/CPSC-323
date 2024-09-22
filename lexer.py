import logging

# Set up advanced logging configuration
logging.basicConfig(
    filename='lexer.log',  # Log messages will be saved to this file
    level=logging.DEBUG,   # Set the logging level to DEBUG to capture detailed info
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log message format
    filemode='w'  # Overwrite the log file each time
)

# List of keywords for RAT24F
keywords = ["integer", "if", "else", "fi", "while", "return", "get", "put"]

# Define operators and separators
operators = ["+", "-", "*", "/", "=", "<", ">", "<=", ">=", "==", "!="]
separators = ["(", ")", "{", "}", ",", ";"]

# Check if the character is a letter for identifier recognition
def is_letter(char):
    return char.isalpha()

# Check if the character is a digit for integer and real recognition
def is_digit(char):
    return char.isdigit()

# Function to skip over comments. Comments in Rat24F are enclosed in [* and *].
# The lexer will ignore everything inside these comment markers.
def handle_comment(source_code, position):
    end_pos = source_code.find("*]", position)
    if end_pos == -1:
        logging.error("Unterminated comment block detected.")
        raise ValueError("Unterminated comment block")
    # Move the position pointer to just after the comment ends.
    logging.debug(f"Comment block ends at position {end_pos}")
    return end_pos + 2  # Skip past the closing comment tag

# This function extracts an identifier from the source code.
# Identifiers must start with a letter and can be followed by letters or digits.
def get_identifier(source_code, position):
    lexeme = ""
    while position < len(source_code) and (source_code[position].isalnum() or source_code[position] == '_'):
        lexeme += source_code[position]
        position += 1
    logging.debug(f"Identifier detected: {lexeme}")
    return lexeme

# This function handles both integers and real numbers.
# If it encounters a '.', it classifies the number as a real number.
def get_number(source_code, position):
    lexeme = ""
    is_real = False  # Flag to check if the number is real or integer
    
    # Loop to capture digits for the integer part.
    while position < len(source_code) and source_code[position].isdigit():
        lexeme += source_code[position]
        position += 1
    
    # If we encounter a dot (.), it's a real number.
    if position < len(source_code) and source_code[position] == '.':
        is_real = True
        lexeme += '.'
        position += 1
        # Capture the digits after the decimal point.
        while position < len(source_code) and source_code[position].isdigit():
            lexeme += source_code[position]
            position += 1
    
    logging.debug(f"Number detected: {lexeme}, Real: {is_real}")
    return lexeme, is_real

# Function to handle operators.
# It checks if an operator is single-character (like +, -) or multi-character (like <=, >=).
def get_operator(source_code, position):
    # Check for two-character operators first (e.g., <=, >=, ==)
    if source_code[position:position+2] in operators:
        return source_code[position:position+2]
    # If it's a single-character operator (e.g., +, -), return it.
    elif source_code[position] in operators:
        return source_code[position]
    return ""

# Main lexer function to identify the input characters one by one
def lexer(source_code):
    position = 0
    tokens = []

    logging.info("Lexer started processing source code.")  # Log start of processing

    while position < len(source_code):
        char = source_code[position]
        logging.debug(f"Processing character: '{char}' at position {position}")  # Log each character being processed

        # Ignore white spaces like tabs, newlines, and spaces.
        if char.isspace():
            logging.debug(f"Skipping whitespace at position {position}")
            position += 1
            continue

        # Comment handler
        if char == '[' and source_code[position+1] == '*':
            logging.info("Comment block detected.")
            position = handle_comment(source_code, position)
            logging.debug(f"Skipped comment block, new position: {position}")
            continue

        # Handle identifiers
        if is_letter(char):
            lexeme = get_identifier(source_code, position)
            if lexeme in keywords:
                logging.debug(f"Keyword detected: {lexeme}")
                tokens.append(("keyword", lexeme))
            else:
                logging.debug(f"Identifier detected: {lexeme}")
                tokens.append(("identifier", lexeme))
            position += len(lexeme)  # Move position forward after processing identifier
            continue

        # Handle numbers (both integers and real numbers).
        if is_digit(char):
            lexeme, is_real = get_number(source_code, position)
            if is_real:
                logging.debug(f"Real number detected: {lexeme}")
                tokens.append(("real", lexeme))
            else:
                logging.debug(f"Integer detected: {lexeme}")
                tokens.append(("integer", lexeme))
            position += len(lexeme)
            continue

        # Handle operators. If the character matches an operator, classify it.
        if any(char == op[0] for op in operators):
            lexeme = get_operator(source_code, position)
            logging.debug(f"Operator detected: {lexeme}")
            tokens.append(("operator", lexeme))
            position += len(lexeme)
            continue

        # Handle separators like parentheses, commas, and semicolons.
        if char in separators:
            logging.debug(f"Separator detected: {char}")
            tokens.append(("separator", char))
            position += 1
            continue

    logging.info("Lexer finished processing source code.")
    return tokens

# Function to read source code from a file.
# This will allow us to test the lexer with actual Rat24F code files.
def read_source_code(filename):
    logging.info(f"Reading source code from file: {filename}")
    try:
        with open(filename, 'r') as file:
            return file.read()
    except FileNotFoundError:
        logging.error(f"File not found: {filename}")
        raise

# Main function to run the lexer on a source code file.
# It reads the source code, calls the lexer, and prints the tokens and lexemes.
if __name__ == "__main__":
    logging.info("Lexer program started.")
    source_code = read_source_code('testcase3.txt')  # Read from test file
    tokens = lexer(source_code)  # Run the lexer
    
    # Output the tokens and lexemes
    for token, lexeme in tokens:
        print(f"Token: {token}, Lexeme: {lexeme}")
    
    logging.info("Lexer program completed.")
