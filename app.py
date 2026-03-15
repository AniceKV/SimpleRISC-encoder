import streamlit as st
import pandas as pd
import label_address_parser
import encoder
import address_allocator
from assembler_error import AssemblerError

st.title("Assembly Encoder")

tab1, tab2 = st.tabs(["Type Code", "Upload File"])

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
            with open("assembly_input.txt", "w") as f:
                f.write(assembly_code)

            address_allocator.allocate_addresses("assembly_input.txt", "program.txt")

            with open("program.txt") as f:
                program = [line.rstrip("\n") for line in f.readlines()]

            subroutine_map = label_address_parser.build_symbol_table(program)
            rows = []

            for line in program:
                stripped = line.strip()
                if stripped == '' or stripped[0] == '.':
                    continue
                parts = line.split(None, 1)
                encoding = encoder.encode(line, subroutine_map).replace("_", "")
                rows.append({"Address": parts[0], "Encoding": encoding})

            df = pd.DataFrame(rows)
            st.success(f"Assembly successful — {len(rows)} instructions encoded.")
            st.dataframe(df, use_container_width=True)
            st.download_button("Download CSV", df.to_csv(index=False), "output.csv", "text/csv")

        except AssemblerError as e:
            st.error(f"Assembler Error: {e}")