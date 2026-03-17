from assembler_error import AssemblerError
import re
def normalize_labels(line):
    return re.sub(r'(\.\w+)\s*:\s*', r'\1', line)

def build_symbol_table(program_lines):
    symbol_table = {}
    current_label = None

    for line in program_lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith('.'):
            if line in symbol_table:
                raise AssemblerError(f"Duplicate label '{line}'")
            current_label = line
            current_label=normalize_labels(line)

        elif line.startswith('0x'):
            parts = line.split(None, 1)
            address = (parts[0])

            if current_label and current_label not in symbol_table:
                symbol_table[current_label] = address
                current_label = None

    return symbol_table

