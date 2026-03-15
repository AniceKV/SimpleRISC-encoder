

import sys


def allocate_addresses(input_path, output_path, start_address=0x0000):
    with open(input_path, 'r') as f:
        lines = [line.rstrip('\n') for line in f.readlines()]

    output_lines = []
    current_address = start_address

    for line in lines:
        stripped = line.strip()

        # Blank line — preserve as-is
        if stripped == '':
            output_lines.append('')
            continue

        # Label declaration — copy through unchanged, no address assigned
        if stripped.startswith('.'):
            output_lines.append(stripped)
            continue

        # Instruction — prepend the current address, then advance by 4
        address_str = f"0x{current_address:04X}"
        output_lines.append(f"{address_str}  {stripped}")
        current_address += 4

    with open(output_path, 'w') as f:
        f.write('\n'.join(output_lines))
        if output_lines:          # ensure trailing newline
            f.write('\n')

    print(f"Address allocation complete.")
    print(f"  Input  : {input_path}")
    print(f"  Output : {output_path}")
    print(f"  Range  : 0x{start_address:04X} – 0x{current_address - 4:04X}  "
          f"({(current_address - start_address) // 4} instruction(s))")


def main():
    input_path   = sys.argv[1] if len(sys.argv) > 1 else 'assembly_input.txt'
    output_path  = sys.argv[2] if len(sys.argv) > 2 else 'program.txt'
    start_addr   = int(sys.argv[3], 0) if len(sys.argv) > 3 else 0x0000

    try:
        allocate_addresses(input_path, output_path, start_addr)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
