#!/usr/bin/env python3
"""
Walks the submission directory and creates a parallel directory of
the tokenized files.

"""

import argparse
import os
import json
import hashlib
from pathlib import Path
import humanize
import datetime


def parse_args():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("basepath")
    return parser.parse_args()


def hasher(lichen_config, lichen_run_config, my_tokenized_file, my_hashes_file):
    language = lichen_run_config["language"]
    hash_size = int(lichen_run_config["hash_size"])

    data_json_path = Path(Path(__file__).resolve().parent.parent,
                          "tokenizer", "tokenizer_config.json")
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
                    token_values[x:x+hash_size]).encode())
                    .hexdigest())[0:8] for x in range(0, num-hash_size+1)]

                if len(token_hashed_values) > lichen_config["max_sequences_per_file"]:
                    token_hashed_values = token_hashed_values[slice(0, lichen_config["max_sequences_per_file"])]  # noqa E501
                    print(f"File {my_hashes_file} truncated after exceeding max sequence limit")

                my_hf.write('\n'.join(token_hashed_values))


def main():
    start_time = datetime.datetime.now()
    args = parse_args()

    with open(Path(args.basepath, "config.json")) as lichen_run_config_file:
        lichen_run_config = json.load(lichen_run_config_file)

    with open(Path(Path(__file__).resolve().parent.parent,
                   'bin', 'lichen_config.json')) as lichen_config_file:
        lichen_config = json.load(lichen_config_file)

    print("HASH ALL:", flush="True")
    print("[0%                      25%                     50%                     75%                     100%]\n[", end="", flush=True)  # noqa: E501

    users_dir = os.path.join(args.basepath, "users")
    if not os.path.isdir(users_dir):
        raise SystemExit("ERROR: Unable to find users directory")

    other_gradeables_dir = os.path.join(args.basepath, "other_gradeables")
    if not os.path.isdir(other_gradeables_dir):
        raise SystemExit("ERROR: Unable to find other gradeables directory")

    total_users = len(os.listdir(users_dir))
    for dir in os.listdir(other_gradeables_dir):
        total_users += len(os.listdir(os.path.join(other_gradeables_dir, dir)))

    users_hashed = 0
    percent_progress = 0

    # ==========================================================================
    # walk the subdirectories of this gradeable

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

        users_hashed += 1
        if int((users_hashed / total_users) * 100) > percent_progress:
            new_percent_progress = int((users_hashed / total_users) * 100)
            print("|" * (new_percent_progress - percent_progress), end="", flush=True)
            percent_progress = new_percent_progress

    # ==========================================================================
    # walk the subdirectories of the other gradeables

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

            users_hashed += 1
            if int((users_hashed / total_users) * 100) > percent_progress:
                new_percent_progress = int((users_hashed / total_users) * 100)
                print("|" * (new_percent_progress - percent_progress), end="", flush=True)
                percent_progress = new_percent_progress

    # ==========================================================================
    # hash the provided code
    provided_code_tokenized = Path(args.basepath, "provided_code", "tokens.json")
    provided_code_hashed = Path(args.basepath, "provided_code", "hashes.txt")
    hasher(lichen_config, lichen_run_config, provided_code_tokenized, provided_code_hashed)

    # ==========================================================================
    print("]\nHashing done in", humanize.precisedelta(start_time, format="%1.f"))


if __name__ == "__main__":
    main()
