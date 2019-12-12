import json
import re
import sys

if len(sys.argv) < 2:
    print(f"USAGE: python3 {sys.argv[0]} path/to/input/file")
    sys.exit(1)

with open(sys.argv[1], "r") as file:
    file_lines = file.readlines()

separators = ' #\n\$",'  # these always signify the end of a non-string token
string_re = re.compile('".+?"')
label_re = re.compile('^[^#"]+?:')
dot_type_re = re.compile(f"^\.[^{separators}]+?[{separators}]")
register_re = re.compile(f'^\$[^#"]+?[{separators}]')
immediate_re = re.compile(f"^\d+?[{separators}]")
# instructions and addresses are combined since they match the same regex
instruction_and_address_re = re.compile(f"^[^#]+?[{separators}]")

token_types = [
    ("STRING_LITERAL", string_re),
    ("LABEL", label_re),
    ("DOT_TYPE", dot_type_re),
    ("REGISTER", register_re),
    ("IMMEDIATE", immediate_re),
    ("INSTRUCTION_ADDRESS", instruction_and_address_re),
]

tokens = []

for line_num, line in enumerate(file_lines):
    col_num = 0
    found_instruction = False
    while col_num < len(line):
        if line[col_num] == "#":
            token = {
                "line": line_num + 1,
                "char": col_num + 1,
                "type": "COMMENT",
                "value": line[col_num:-1],
            }
            tokens.append(token)
            break
        elif str.isspace(line[col_num]):
            col_num += 1
            continue

        # Attempt to match any token type.  Tokens are ordered by specificity,
        # so the first match is always correct
        for token_type, token_re in token_types:
            token_match = token_re.match(line[col_num:])
            if token_match:
                if token_type == "INSTRUCTION_ADDRESS" and not found_instruction:
                    token_type = "INSTRUCTION"
                    found_instruction = True
                elif token_type == "INSTRUCTION_ADDRESS":
                    token_type = "ADDRESS"

                token = {}
                token["line"] = line_num + 1
                token["char"] = col_num + 1
                token["type"] = token_type

                col_num += len(token_match[0]) - 1

                token_val = token_match[0].strip()

                # Correct stray characters
                if token_type == "LABEL" or token_val[-1] == ",":
                    token_val = token_val[:-1]
                elif token_val[-1] == "$" or token_val[-1] == "#":
                    token_val = token_val[:-1]
                    col_num -= 1

                token["value"] = token_val

                tokens.append(token)

                break

        col_num += 1

print(json.dumps(tokens, indent=4, sort_keys=True))
