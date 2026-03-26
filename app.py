import streamlit as st
import pandas as pd
import label_address_parser
import encoder
import address_allocator
from assembler_error import AssemblerError


def to_intel_hex(df):
    lines = []

    for _, row in df.iterrows():
        # Parse address — supports 0x hex or plain decimal
        addr_str = row["Address"]
        address = int(addr_str, 16) if addr_str.startswith("0x") or addr_str.startswith("0X") else int(addr_str)

        # Convert binary string to bytes
        binary_str = row["Encoding"].replace(" ", "")
        # Pad to a multiple of 8 bits
        pad = (8 - len(binary_str) % 8) % 8
        binary_str = "0" * pad + binary_str
        data_bytes = [int(binary_str[i:i+8], 2) for i in range(0, len(binary_str), 8)]

        byte_count = len(data_bytes)
        addr_high = (address >> 8) & 0xFF
        addr_low  = address & 0xFF
        record_type = 0x00  # data record

        # Checksum: two's complement of (sum of all bytes in the record) & 0xFF
        checksum_input = [byte_count, addr_high, addr_low, record_type] + data_bytes
        checksum = ((~sum(checksum_input) + 1) & 0xFF)

        data_hex = "".join(f"{b:02X}" for b in data_bytes)
        line = f":{byte_count:02X}{addr_high:02X}{addr_low:02X}{record_type:02X}{data_hex}{checksum:02X}"
        lines.append(line)

    # EOF record
    lines.append(":00000001FF")
    return "\n".join(lines)


st.title("Assembly Encoder")

tab1, tab2 = st.tabs(["Type Code", "Upload File"])

assembly_code = ""

with tab1:
    assembly_code = st.text_area("Write assembly code", height=300)

with tab2:
    uploaded_file = st.file_uploader("Upload .txt file", type=["txt"])
    if uploaded_file is not None:
        assembly_code = uploaded_file.read().decode("utf-8")
        st.text_area("Preview", assembly_code, height=300, disabled=True)

if st.button("Assemble"):
    if not assembly_code.strip():
        st.error("No input provided.")
    else:
        try:
            # Save input temporarily
            with open("assembly_input.txt", "w") as f:
                f.write(assembly_code)

            # Allocate addresses
            address_allocator.allocate_addresses("assembly_input.txt", "program.txt")

            # Read processed program
            with open("program.txt") as f:
                program = [line.rstrip("\n") for line in f.readlines()]

            # Build symbol table
            subroutine_map = label_address_parser.build_symbol_table(program)

            rows = []

            for line in program:
                stripped = line.strip()

                # Skip comments / empty lines
                if stripped == '' or stripped[0] == '.' or stripped[0] == '/':
                    continue

                parts = line.split(None, 1)

                encoding = encoder.encode(line, subroutine_map).replace("_", "")

                rows.append({
                    "Address": parts[0],
                    "Encoding": encoding
                })

            # DataFrame display
            df = pd.DataFrame(rows)

            st.success(f"Assembly successful — {len(rows)} instructions encoded.")
            st.dataframe(df, use_container_width=True)

            col1, col2 = st.columns(2)

            # ---- TXT OUTPUT ----
            text_output = "\n".join(
                f"{row['Address']} {row['Encoding']}" for _, row in df.iterrows()
            )

            with col1:
                st.download_button(
                    "Download TXT",
                    text_output,
                    "output.txt",
                    "text/plain",
                    use_container_width=True
                )

            # ---- INTEL HEX OUTPUT ----
            hex_output = to_intel_hex(df)

            with col2:
                st.download_button(
                    "Download Intel HEX",
                    hex_output,
                    "output.hex",
                    "text/plain",
                    use_container_width=True
                )

        except AssemblerError as e:
            st.error(f"Assembler Error: {e}")