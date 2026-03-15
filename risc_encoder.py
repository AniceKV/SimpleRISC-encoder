import sys
import label_address_parser
import encoder
from assembler_error import AssemblerError
import address_allocator

address_allocator.allocate_addresses('assembly_input.txt', 'program.txt')

with open('program.txt', 'r') as f:
    program = [line.rstrip('\n') for line in f.readlines()]

# Build symbol table (catches duplicate labels)
try:
    subroutine_map = label_address_parser.build_symbol_table(program)
except AssemblerError as e:
    print(e, file=sys.stderr)
    sys.exit(1)

# Track the 1-based instruction line number (skipping labels and blanks)
instruction_line_number = 0

with open('output.txt','w') as f:
    for line in program:
        stripped = line.strip()
        if stripped == '':
            continue
        elif stripped[0] == '.':
            continue
        else:
            instruction_line_number += 1
            try:
                parts = line.split(None, 1)
                current_location = parts[0]
                encoding = encoder.encode(line, subroutine_map).replace('_', '')
                f.write(f"{current_location} {encoding}\n")
            except AssemblerError as e:
                # Attach the instruction line number and re-print
                print(
                    f"Error on instruction line {instruction_line_number}: {e.message}",
                    file=sys.stderr
                )
                sys.exit(1)
