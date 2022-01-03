#!/usr/bin/env python3
"""
Tokenizes the concatenated files.
"""

import argparse
import os
import json
import time
import subprocess


def parse_args():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("basepath")
    return parser.parse_args()


def tokenize(lichen_config_data, my_concatenated_file, my_tokenized_file):
    language = lichen_config_data["language"]

    cli_args = list()
    language_token_data = dict()

    data_json_path = "./data.json"  # data.json is in the Lichen/bin directory after install
    with open(data_json_path, 'r') as token_data_file:
        data_file = json.load(token_data_file)
        language_token_data = data_file[language]
        for argument in lichen_config_data["arguments"]:
            if argument in language_token_data["command_args"]:
                cli_args.append(language_token_data["command_args"][argument]["argument"])
            else:
                print(f"Error: Unknown tokenization argument {argument}")

    tokenizer = f"./{language_token_data['tokenizer']}"

    result = subprocess.run([language_token_data['command_executable'],
                             tokenizer, my_concatenated_file, cli_args],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)

    stderr = result.stderr.decode('utf-8')
    if not stderr.isspace() and stderr is not None and stderr != '':
        print(result.stderr.decode("utf-8"))

    with open(my_tokenized_file, 'w') as file:
        file.write(result.stdout.decode('utf-8'))


def main():
    start_time = time.time()
    args = parse_args()

    print("TOKENIZE ALL...", end="", flush=True)

    with open(os.path.join(args.basepath, "config.json")) as lichen_config:
        lichen_config_data = json.load(lichen_config)

    # ===========================================================================
    # walk the subdirectories to tokenize this gradeable's submissions
    users_dir = os.path.join(args.basepath, "users")
    if not os.path.isdir(users_dir):
        raise SystemExit("ERROR! Unable to find users directory")

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
    # tokenize the other other gradeables' submissions
    other_gradeables_dir = os.path.join(args.basepath, "other_gradeables")
    if not os.path.isdir(other_gradeables_dir):
        raise SystemExit("ERROR! Unable to find other gradeables directory")

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
