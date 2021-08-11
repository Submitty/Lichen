#!/usr/bin/env python3
"""
Walks the submission directory and creates a parallel directory of
the tokenized files.

"""

import argparse
import os
import json
import time
import hashlib
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("basepath")
    return parser.parse_args()


def hasher(lichen_config, lichen_run_config, my_tokenized_file, my_hashes_file):
    language = lichen_run_config["language"]
    sequence_length = int(lichen_run_config["sequence_length"])

    data_json_path = "./data.json"  # data.json is in the Lichen/bin directory after install
    with open(data_json_path) as token_data_file:
        token_data = json.load(token_data_file)

    with open(my_tokenized_file, 'r', encoding='ISO-8859-1') as my_tf:
        with open(my_hashes_file, 'w') as my_hf:
            tokens = json.load(my_tf)
            # write empty hashes file if the tokens file was empty (such as
            # when there is no provided code)
            if tokens is not None:
                token_values = [str(x[token_data[language]["token_value"]]) for x in tokens]
                num = len(tokens)
                # FIXME: this truncation should be adjusted after testing
                token_hashed_values = [(hashlib.md5(''.join(
                    token_values[x:x+sequence_length]).encode())
                    .hexdigest())[0:8] for x in range(0, num-sequence_length+1)]

                if len(token_hashed_values) > lichen_config["max_sequences_per_file"]:
                    token_hashed_values = token_hashed_values[slice(0, lichen_config["max_sequences_per_file"])] #noqa E501
                    print(f"File {my_hashes_file} truncated after exceeding max sequence limit")

                my_hf.write('\n'.join(token_hashed_values))


def main():
    start_time = time.time()
    args = parse_args()

    with open(Path(args.basepath, "config.json")) as lichen_run_config_file:
        lichen_run_config = json.load(lichen_run_config_file)

    with open(Path(__file__).resolve().parent / "lichen_config.json") as lichen_config_file:
        lichen_config = json.load(lichen_config_file)

    print("HASH ALL...", end="")

    # ==========================================================================
    # walk the subdirectories of this gradeable
    users_dir = Path(args.basepath, "users")
    if not os.path.isdir(users_dir):
        raise SystemExit("ERROR! Unable to find users directory")

    for user in sorted(os.listdir(users_dir)):
        user_dir = Path(users_dir, user)
        if not os.path.isdir(user_dir):
            continue

        for version in sorted(os.listdir(user_dir)):
            my_dir = Path(user_dir, version)
            if not os.path.isdir(my_dir):
                continue

            my_tokenized_file = Path(my_dir, "tokens.json")
            my_hashes_file = Path(my_dir, "hashes.txt")
            hasher(lichen_config, lichen_run_config, my_tokenized_file, my_hashes_file)

    # ==========================================================================
    # walk the subdirectories of the other gradeables

    other_gradeables_dir = Path(args.basepath, "other_gradeables")
    if not os.path.isdir(other_gradeables_dir):
        raise SystemExit("ERROR! Unable to find other gradeables directory")

    for other_gradeable in sorted(os.listdir(other_gradeables_dir)):
        other_gradeable_dir = Path(other_gradeables_dir, other_gradeable)
        if not os.path.isdir(other_gradeable_dir):
            continue

        for other_user in sorted(os.listdir(other_gradeable_dir)):
            other_user_dir = Path(other_gradeable_dir, other_user)
            if not os.path.isdir(other_user_dir):
                continue

            for other_version in sorted(os.listdir(other_user_dir)):
                other_version_dir = Path(other_user_dir, other_version)
                if not os.path.isdir(other_version_dir):
                    continue

                other_tokenized_file = Path(other_version_dir, "tokens.json")
                other_hashes_file = Path(other_version_dir, "hashes.txt")
                hasher(lichen_config, lichen_run_config, other_tokenized_file, other_hashes_file)

    # ==========================================================================
    # hash the provided code
    provided_code_tokenized = Path(args.basepath, "provided_code", "tokens.json")
    provided_code_hashed = Path(args.basepath, "provided_code", "hashes.txt")
    hasher(lichen_config, lichen_run_config, provided_code_tokenized, provided_code_hashed)

    # ==========================================================================
    end_time = time.time()
    print("done in " + "%.0f" % (end_time - start_time) + " seconds")


if __name__ == "__main__":
    main()
