import clang.cindex
import json
import shutil
import tempfile
import os
import argparse


def parse_args():
    parser = argparse.ArgumentParser(description='C Tokenizer')
    parser.add_argument('input_file')
    parser.add_argument('--ignore_comments', action='store_true')
    return parser.parse_args()


def main():
    args = parse_args()

    # apparently, the file name must end in .cpp (or some standard
    # c/c++ suffix to be successfully tokenized)

    # make a temprary filename
    tmp_cpp_file_handle, tmp_cpp_file_name = tempfile.mkstemp(suffix='.cpp')
    # copy the concatenated file to the temporary file location
    shutil.copy(args.input_file, tmp_cpp_file_name)

    if (os.path.isfile('/usr/lib/llvm-14/lib/libclang.so.1')):
        clang.cindex.Config.set_library_file('/usr/lib/llvm-14/lib/libclang.so.1')
    idx = clang.cindex.Index.create()

    # parse the input file
    parsed_data = idx.parse(tmp_cpp_file_name)

    # remove the temporary file
    os.remove(tmp_cpp_file_name)

    tokens = []

    for token in parsed_data.get_tokens(extent=parsed_data.cursor.extent):
        tmp = dict()
        tmp['line'] = int(token.location.line)
        tmp['char'] = int(token.location.column)
        tmp['type'] = (str(token.kind))[10:]
        if tmp['type'] == 'PUNCTUATION':
            tmp['type'] += '-' + str(token.spelling)
        tmp['value'] = str(token.spelling)

        if args.ignore_comments and tmp['type'] == 'COMMENT':
            continue

        tokens.append(tmp)

    print(json.dumps(tokens, indent=4, sort_keys=True))


if __name__ == '__main__':
    main()
