#!/usr/bin/env python3
"""
Tokenizes the concatenated files.
"""

import argparse
import os
import json
import time
import sys


def parse_args():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("basepath")
    return parser.parse_args()


def tokenize(lichen_config_data, my_concatenated_file, my_tokenized_file):
    language = lichen_config_data["language"]

    language_token_data = dict()

    data_json_path = "./data.json"  # data.json is in the Lichen/bin directory after install
    with open(data_json_path, 'r') as token_data_file:
        token_data = json.load(token_data_file)
        language_token_data = token_data[language]

    tokenizer = f"./{language_token_data['tokenizer']}"

    if not language_token_data.get("input_as_argument"):
        my_concatenated_file = f'< {my_concatenated_file}'
    cli_args = ' '.join(language_token_data["command_args"])\
               if "command_args" in language_token_data else ''

    command = f'{language_token_data["command_executable"]} {tokenizer} {cli_args}\
                    {my_concatenated_file} > {my_tokenized_file}'.strip()
    os.system(command)


def main():
    start_time = time.time()
    args = parse_args()

    sys.stdout.write("TOKENIZE ALL...")
    sys.stdout.flush()

    with open(os.path.join(args.basepath, "config.json")) as lichen_config:
        lichen_config_data = json.load(lichen_config)

    # ===========================================================================
    # walk the subdirectories to tokenize this gradeable's submissions
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

            my_concatenated_file = os.path.join(my_dir, "submission.concatenated")
            my_tokenized_file = os.path.join(my_dir, "tokens.json")
            tokenize(lichen_config_data, my_concatenated_file, my_tokenized_file)

    # ===========================================================================
    # tokenize the other prior term gradeables' submissions
    other_gradeables_dir = os.path.join(args.basepath, "other_gradeables")
    if not os.path.isdir(other_gradeables_dir):
        print("Error: Unable to find other gradeables directory")
        exit(1)

    for other_gradeable in sorted(os.listdir(other_gradeables_dir)):
        other_gradeable_dir = os.path.join(other_gradeables_dir, other_gradeable)
        if not os.path.isdir(other_gradeable_dir):
            continue

        for other_user in sorted(os.listdir(other_gradeable_dir)):
            other_user_dir = os.path.join(other_gradeable_dir, other_user)
            if not os.path.isdir(other_user_dir):
                continue

            for other_version in sorted(os.listdir(other_user_dir)):
                other_version_dir = os.path.join(other_user_dir, other_version)
                if not os.path.isdir(other_version_dir):
                    continue

                other_concatenated_file = os.path.join(other_version_dir, "submission.concatenated")
                other_tokenized_file = os.path.join(other_version_dir, "tokens.json")
                tokenize(lichen_config_data, other_concatenated_file, other_tokenized_file)

    # ===========================================================================
    # tokenize the provided code
    provided_code_concat = os.path.join(args.basepath, "provided_code", "submission.concatenated")
    provided_code_tokenized = os.path.join(args.basepath, "provided_code", "tokens.json")
    tokenize(lichen_config_data, provided_code_concat, provided_code_tokenized)

    # ==========================================================================
    end_time = time.time()
    print("done in " + "%.0f" % (end_time - start_time) + " seconds")


if __name__ == "__main__":
    main()
