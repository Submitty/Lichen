import json
import argparse
import string


def parse_args():
    parser = argparse.ArgumentParser(description="Plaintext Tokenizer")
    parser.add_argument("input_file")
    parser.add_argument("--ignore_punctuation", action='store_true')
    parser.add_argument("--to_lower", action='store_true')
    parser.add_argument("--ignore_numbers", action='store_true')
    parser.add_argument("--ignore_newlines", action='store_true')
    return parser.parse_args()


def main():
    args = parse_args()

    with open(args.input_file, "r", encoding="ISO-8859-1") as input_file:
        file_data = input_file.read()

    tokens = []
    token = ""
    row = 1
    col = 1
    start_row = -1
    start_col = -1
    last_was_alpha = False
    last_was_digit = False
    for char in file_data:
        is_punctuation = char in string.punctuation

        # ----------------------------------------------------------------------
        # decide when to break the current string
        # break on spaces, punctuation (any symbol), or if we switch between letters and numbers
        if (char.isspace() or is_punctuation
                or (last_was_alpha and char.isdigit()) or (last_was_digit and char.isalpha())):
            # save this token
            if token != "":
                tmp = {}
                tmp["line"] = start_row
                tmp["char"] = start_col
                if (last_was_digit):
                    assert not last_was_alpha
                    # check to see if this will fit in an int -- otherwise treat it as a string
                    try:
                        tmp["value"] = int(token)
                        tmp["type"] = "number"
                    except Exception:
                        tmp["value"] = token
                        tmp["type"] = "string"
                else:
                    assert last_was_alpha
                    tmp["value"] = token
                    tmp["type"] = "string"

                tokens.append(tmp)
                token = ""
                last_was_alpha = False
                last_was_digit = False

        # ----------------------------------------------------------------------
        # decide whether to add this character to the current string
        if char.isspace():
            pass  # never add spaces
        # ------------------------------
        elif is_punctuation:
            assert token == ""
            assert not last_was_alpha
            assert not last_was_digit

            # only add punctuation if its not being ignored
            # (punctuation is always a single symbol character per token)
            if not args.ignore_punctuation:
                tmp = {}
                tmp["line"] = row
                tmp["char"] = col
                tmp["type"] = "punctuation"
                tmp["value"] = char
                tokens.append(tmp)
        # ------------------------------
        elif char.isdigit():
            assert not last_was_alpha
            # only add digits/numbers if they are not being ignored
            # numbers will be 1 or more digits 0-9.
            # We break tokens between letters & numbers.
            if not args.ignore_numbers:
                if token == "":
                    start_row = row
                    start_col = col
                    last_was_digit = True
                else:
                    assert last_was_digit
                token += char
        # ------------------------------
        elif char.isalpha():
            assert not last_was_digit
            if token == "":
                start_row = row
                start_col = col
                last_was_alpha = True
            else:
                assert last_was_alpha

            # to_lower argument
            if args.to_lower:
                char = char.lower()

            token += char

        # ----------------------------------------------------------------------
        if char == "\n":
            assert token == ""
            if not args.ignore_newlines:
                # output a token for the newline
                tmp = {}
                tmp["line"] = row
                tmp["char"] = col
                tmp["type"] = "newline"
                tmp["value"] = "\n"
                tokens.append(tmp)
            # advance to the next row/line
            row += 1
            col = 1
        else:
            col += 1
    # --------------------------------------------------------------------------
    # print the json file
    print(json.dumps(tokens, indent=4, sort_keys=True))


# Run tokenizer
main()
