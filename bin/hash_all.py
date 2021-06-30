#!/usr/bin/env python3
"""
Walks the submission directory and creates a parallel directory of
the tokenized files.

"""

import argparse
import os
import json
import time
import sys
import hashlib


def parse_args():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("basepath")
    return parser.parse_args()


def hasher(lichen_config_data, my_tokenized_file, my_hashes_file):
    language = lichen_config_data["language"]
    sequence_length = int(lichen_config_data["sequence_length"])

    data_json_path = "./data.json"  # data.json is in the Lichen/bin directory after install
    with open(data_json_path) as token_data_file:
        token_data = json.load(token_data_file)
        if language not in token_data:
            print("\n\nERROR: UNKNOWN HASHER\n\n")
            exit(1)

    if (sequence_length < 1):
        print("ERROR! sequence_length must be >= 1")
        exit(1)

    with open(my_tokenized_file, 'r', encoding='ISO-8859-1') as my_tf:
        with open(my_hashes_file, 'w') as my_hf:
            tokens = json.load(my_tf)
            token_values = [str(x.get(token_data[language]["token_value"]))
                            for x in tokens]
            num = len(tokens)
            # FIXME: this truncation should be adjusted after testing
            token_hashed_values = [(hashlib.md5(''.join(
                token_values[x:x+sequence_length]).encode())
                .hexdigest())[0:8] for x in range(0, num-sequence_length+1)]

            my_hf.write('\n'.join(token_hashed_values))


def main():
    start_time = time.time()
    args = parse_args()

    with open(os.path.join(args.basepath, "config.json")) as lichen_config:
        lichen_config_data = json.load(lichen_config)

    sys.stdout.write("HASH ALL...")
    sys.stdout.flush()

    # =========================================================================
    # walk the subdirectories
    users_dir = os.path.join(args.basepath, "users")
    if not os.path.isdir(users_dir):
        print("Error: Unable to find users directory")
        exit(1)

    for user in sorted(os.listdir(users_dir)):
        user_dir = os.path.join(users_dir, user)
        if not os.path.isdir(user_dir):
            continue

        for version in sorted(os.listdir(user_dir)):
            my_dir = os.path.join(user_dir, version)
            if not os.path.isdir(my_dir):
                continue

            my_tokenized_file = os.path.join(my_dir, "tokens.json")
            my_hashes_file = os.path.join(my_dir, "hashes.txt")
            hasher(lichen_config_data, my_tokenized_file, my_hashes_file)

    # ===========================================================================
    # hash the provided code
    provided_code_tokenized = os.path.join(args.basepath, "provided_code", "tokens.json")
    provided_code_hashed = os.path.join(args.basepath, "provided_code", "hashes.txt")
    hasher(lichen_config_data, provided_code_tokenized, provided_code_hashed)

    # ==========================================================================
    end_time = time.time()
    print("done in " + "%.0f" % (end_time - start_time) + " seconds")


if __name__ == "__main__":
    main()
