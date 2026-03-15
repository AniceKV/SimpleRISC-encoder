import re
from assembler_error import AssemblerError

opcode_map = {
    "add":  "00000",
    "sub":  "00001",
    "mul":  "00010",
    "div":  "00011",
    "mod":  "00100",
    "cmp":  "00101",
    "and":  "00110",
    "or":   "00111",

    "not":  "01000",
    "mov":  "01001",
    "lsl":  "01010",
    "lsr":  "01011",
    "asr":  "01100",
    "nop":  "01101",
    "ld":   "01110",
    "st":   "01111",

    "beq":  "10000",
    "bgt":  "10001",
    "b":    "10010",
    "call": "10011",
    "ret":  "10100",
}

# Expected number of tokens (opcode + operands) for each instruction.
# type-1 branches have 2 tokens: opcode + label
# type-0 (ret, nop) have 1 token: opcode only
_expected_token_counts = {
    "ret":  1, "nop":  1,
    "b":    2, "call": 2, "beq": 2, "bgt": 2,
    "not":  3, "mov":  3, "cmp": 3,
    "ld":   3, "st":   3,
    "add":  4, "sub":  4, "mul": 4, "div": 4, "mod": 4,
    "and":  4, "or":   4, "lsl": 4, "lsr": 4, "asr": 4,
}


def get_encoding_type(opcode):
    if opcode in ("ret", "nop"):
        return 0
    elif opcode in ("call", "b", "beq", "bgt"):
        return 1
    elif opcode in ("add", "sub", "mul", "div", "mod", "and", "or", "lsl", "lsr", "asr"):
        return 3
    else:
        return 2


def set_Imm_flag(instruction):
    try:
        int(instruction, 0)
        return 1
    except ValueError:
        return 0


def register_text_to_encoding(text):
    """Convert a register token like 'r3' to a 4-bit binary string.
    Raises AssemblerError if the register number is out of range (0-15).
    """
    match = re.search(r'\d+', text)
    if match:
        number = int(match.group())
        if number > 15:
            raise AssemblerError(
                f"Register out of range: '{text}' (SimpleRISC supports r0–r15)"
            )
        return format(number, '04b')
    else:
        return '0000'


def to_16bit_binary(val):
    return format(int(val, 0), '016b')


def to_18bit_binary(val):
    return format(int(val, 0), '018b')


def pad_to_32_bits(code):
    bit_count = len(code.replace('_', ''))
    return code + '0' * (32 - bit_count)


def to_2s_complement(value, bits):
    if value < 0:
        value = (1 << bits) + value
    return format(value, f'0{bits}b')


# ---------------------------------------------------------------------------
# Operand-count guard
# ---------------------------------------------------------------------------

def _check_operand_count(instruction_tokens):
    op = instruction_tokens[0].lower()
    expected = _expected_token_counts.get(op)
    if expected is None:
        return  # unknown opcode is caught earlier
    actual = len(instruction_tokens)
    if actual != expected:
        operand_expected = expected - 1
        operand_actual = actual - 1
        raise AssemblerError(
            f"Wrong number of operands for '{op}': "
            f"expected {operand_expected}, got {operand_actual}"
        )


# ---------------------------------------------------------------------------
# Encoding helpers
# ---------------------------------------------------------------------------

def encoding_type_0(instruction_tokens, current_location=None, subroutine_map=None):
    _check_operand_count(instruction_tokens)
    code = opcode_map[instruction_tokens[0].lower()]
    code = code.ljust(32, '0')
    return code


def encoding_type_1(instruction_tokens, current_location, subroutine_map):
    _check_operand_count(instruction_tokens)
    op = instruction_tokens[0].lower()
    label = instruction_tokens[1].lower()

    # Undefined label
    if label not in subroutine_map:
        raise AssemblerError(f"Undefined label '{label}'")

    label_location = subroutine_map[label]
    offset = (int(label_location, 16) - int(current_location, 16)) // 4

    # Jump offset too large for 27-bit signed field
    max_offset = (1 << 26) - 1   # 2^26 - 1
    min_offset = -(1 << 26)      # -2^26
    if not (min_offset <= offset <= max_offset):
        raise AssemblerError(
            f"Jump offset too large for '{op} {label}': "
            f"offset {offset} does not fit in a 27-bit signed field "
            f"(range {min_offset} to {max_offset})"
        )

    code = ''
    code += opcode_map[op]
    code += '_'
    code += to_2s_complement(offset, 27)
    return code


def encoding_type_2(instruction_tokens, current_location=None, subroutine_map=None):
    _check_operand_count(instruction_tokens)
    code = ''
    op = instruction_tokens[0].lower()

    if op == 'cmp':
        code += opcode_map[op]
        code += '_'
        code += str(set_Imm_flag(instruction_tokens[2]))
        code += '_'
        code += '0000'
        code += '_'
        code += register_text_to_encoding(instruction_tokens[1])
        code += '_'
        if set_Imm_flag(instruction_tokens[2]) == 0:
            code += register_text_to_encoding(instruction_tokens[2])
        else:
            code += '00_'
            code += to_16bit_binary(instruction_tokens[2])

    elif op in ('mov', 'not'):
        code += opcode_map[op]
        code += '_'
        code += str(set_Imm_flag(instruction_tokens[2]))
        code += '_'
        code += register_text_to_encoding(instruction_tokens[1])
        code += '_'
        code += '0000'
        code += '_'
        if set_Imm_flag(instruction_tokens[2]) == 0:
            code += register_text_to_encoding(instruction_tokens[2])
        else:
            code += '00_'
            code += to_16bit_binary(instruction_tokens[2])

    elif op in ('st', 'ld'):
        raw_operand = instruction_tokens[2]

        # Validate ld/st operand format: offset[base_reg]
        if '[' not in raw_operand or ']' not in raw_operand:
            raise AssemblerError(
                f"Malformed operand for '{op}': expected format 'offset[reg]', "
                f"got '{raw_operand}'"
            )

        offset_str = raw_operand.split('[')[0]
        reference = raw_operand.split('[')[1].split(']')[0]

        # Misaligned access check
        try:
            offset_val = int(offset_str, 0)
        except ValueError:
            raise AssemblerError(
                f"Invalid immediate offset for '{op}': '{offset_str}' is not a number"
            )

        if offset_val % 4 != 0:
            raise AssemblerError(
                f"Misaligned access for '{op}': immediate offset {offset_val} "
                f"is not a multiple of 4 (SimpleRISC memory is word-aligned)"
            )

        code += opcode_map[op]
        code += '_1_'
        code += register_text_to_encoding(instruction_tokens[1])
        code += '_'
        code += register_text_to_encoding(reference)
        code += '_'
        code += to_2s_complement(offset_val, 18)

    code = pad_to_32_bits(code)
    return code


def encoding_type_3(instruction_tokens, current_location=None, subroutine_map=None):
    _check_operand_count(instruction_tokens)
    code = ''
    code += opcode_map[instruction_tokens[0].lower()]
    code += '_'
    code += str(set_Imm_flag(instruction_tokens[3]))
    code += '_'
    code += register_text_to_encoding(instruction_tokens[1])
    code += '_'
    code += register_text_to_encoding(instruction_tokens[2])
    code += '_'
    if set_Imm_flag(instruction_tokens[3]) == 0:
        code += register_text_to_encoding(instruction_tokens[3])
    else:
        code += '00_'
        code += to_16bit_binary(instruction_tokens[3])
    code = pad_to_32_bits(code)
    return code


encoding_functions = [encoding_type_0, encoding_type_1, encoding_type_2, encoding_type_3]


def _validate_delimiters(instruction):
    """Detect obvious comma/delimiter problems in the operand portion.

    Rules checked:
    - Consecutive commas  (,,)
    - Leading comma in operand section
    - Trailing comma in operand section
    """
    parts = instruction.split(None, 1)  # [opcode, rest]
    if len(parts) < 2:
        return  # no operands – count check handles this

    rest = parts[1].strip()
    if ',,' in rest:
        raise AssemblerError(
            f"Delimiter error in '{instruction}': consecutive commas ',,'"
        )
    if rest.startswith(','):
        raise AssemblerError(
            f"Delimiter error in '{instruction}': unexpected leading comma"
        )
    if rest.endswith(','):
        raise AssemblerError(
            f"Delimiter error in '{instruction}': unexpected trailing comma"
        )


def encode(line, subroutine_map={}):
    """
    Takes a single line like '0x0008  call .add_nums'
    and subroutine_map like {'.add_nums': '0x0014'}
    Returns the 32-bit binary encoding string.
    Raises AssemblerError for any encoding problem.
    """
    parts = line.split(None, 1)         # ["0x0008", "call .add_nums"]
    current_location = parts[0]         # "0x0008"
    instruction = parts[1]              # "call .add_nums"

    # Delimiter check before tokenising
    _validate_delimiters(instruction)

    instruction_tokens = re.split(r'[,\s]+', instruction.strip())
    op = instruction_tokens[0].lower()

    # Invalid opcode
    if op not in opcode_map:
        raise AssemblerError(f"Invalid opcode '{op}'")

    encoding_type = get_encoding_type(op)
    code = encoding_functions[encoding_type](instruction_tokens, current_location, subroutine_map)
    return code


# --- quick test ---
if __name__ == "__main__":
    subroutine_map = {'.main': '0x0000', '.add_nums': '0x0014'}

    test_lines = [
        "0x0000  mov r1, 5",
        "0x0004  mov r2, 10",
        "0x0008  call .add_nums",
        "0x000C  st r3, 0[r14]",
        "0x0010  ret",
        "0x0014  add r3, r1, r2",
        "0x0018  ret"
    ]

    for line in test_lines:
        print(f"{line.split(None,1)[0]}  →  {encode(line, subroutine_map)}")