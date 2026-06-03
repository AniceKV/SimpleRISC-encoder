Simple RISC Encoder

Web demo: https://simplerisc-encoder.streamlit.app/

This repository implements a small assembler/encoder for a simple RISC-like instruction
set and produces two output formats: a plain TXT listing of addresses + binary encodings,
and an Intel HEX file suitable for flashing or simulation.

Key features
- Web UI via Streamlit (app.py) to paste or upload assembly and download outputs.
- Two-pass assembly approach: symbol table construction and instruction encoding.
- Address allocation stage that normalizes addresses and expands data/instructions.
- Output generation in plain TXT and Intel HEX formats.

Implementation notes
- Parsing & symbol table: label_address_parser.py builds a map of labels/addresses
	from the processed program so branch and subroutine operands can be resolved.
- Address allocation: address_allocator.py processes raw assembly, assigns addresses,
	and writes a linear program.txt that the encoder consumes.
- Encoding: encoder.py exposes encode(line, symbol_table) which returns a binary
	string (may contain separator characters which callers strip) representing the
	machine encoding for a single assembly line.
- App flow: app.py calls address_allocator.allocate_addresses(), builds the
	symbol table, encodes each non-comment line via encoder.encode(), and then
	offers TXT and Intel HEX downloads. The Intel HEX conversion logic lives in
	app.py (function to_intel_hex) and demonstrates byte packing and checksum.

Files overview
- c:\Users\Anish Kumar Verma\PycharmProjects\SimpleRiscEncoding\app.py — Streamlit UI and Intel HEX exporter.
- c:\Users\Anish Kumar Verma\PycharmProjects\SimpleRiscEncoding\address_allocator.py — address allocation / preprocessor.
- c:\Users\Anish Kumar Verma\PycharmProjects\SimpleRiscEncoding\label_address_parser.py — builds symbol table from program.
- c:\Users\Anish Kumar Verma\PycharmProjects\SimpleRiscEncoding\encoder.py — instruction encoding routines.
- c:\Users\Anish Kumar Verma\PycharmProjects\SimpleRiscEncoding\risc_encoder.py — (alternate entry / helpers for encoding).
- c:\Users\Anish Kumar Verma\PycharmProjects\SimpleRiscEncoding\assembler_error.py — custom exception type for assembler errors.
- assembly_input.txt — example input; program.txt and output.txt are generated outputs.

Example
Input (assembly_input.txt):

mov r1,r2
add r1,r2,r3

Using the Streamlit UI (run with `streamlit run app.py`) you can paste the assembly above,
press "Assemble", and download `output.txt` (address + binary encoding per line)
and `output.hex` (Intel HEX format).

Running locally
- Install requirements (Python 3.8+ recommended):

```bash
pip install streamlit pandas
```

- Start the web UI:

```bash
streamlit run app.py
```

Notes & next steps
- The encoding format and instruction set conventions are based on a simple
	educational RISC architecture. The project originally referenced conventions
	from Smruti R Sarangi's Basic Computer Architecture.
- Improvements you may want: a requirements.txt, unit tests for the encoder,
	richer error messages from address_allocator, and more complete instruction
	documentation (opcodes, field layouts).

If you'd like, I can add a requirements file, document the instruction formats
in detail, or add an examples directory with annotated assembly and expected outputs.