#!/usr/bin/env python3
"""
Walks the submission directory and creates a parallel directory of
the concatenated files.
"""

import argparse
import os
import json
import sys
import shutil
import fnmatch

CONFIG_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..', 'config')
with open(os.path.join(CONFIG_PATH, 'submitty.json')) as open_file:
    OPEN_JSON = json.load(open_file)
SUBMITTY_DATA_DIR = OPEN_JSON['submitty_data_dir']
SUBMITTY_INSTALL_DIR = OPEN_JSON['submitty_install_dir']


def parse_args():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("config_path")
    return parser.parse_args()


def main():
    args = parse_args()

    sys.stdout.write("CONCATENATE ALL...")
    sys.stdout.flush()

    with open(args.config_path) as lichen_config:
        lichen_config_data = json.load(lichen_config)
        semester = lichen_config_data["semester"]
        course = lichen_config_data["course"]
        gradeable = lichen_config_data["gradeable"]
        expressions = None
        if("regex" in lichen_config_data):
            # this assumes regex is seperated by a ','
            expressions = lichen_config_data["regex"].split(',')

    # =========================================================================
    # error checking
    course_dir = os.path.join(SUBMITTY_DATA_DIR, "courses", semester, course)
    if not os.path.isdir(course_dir):
        print("ERROR! ", course_dir, " is not a valid course directory")
        exit(1)
    submission_dir = os.path.join(course_dir, "submissions", gradeable)
    if not os.path.isdir(submission_dir):
        print("ERROR! ", submission_dir, " is not a valid gradeable submissions directory")
        exit(1)

    # =========================================================================
    # create the directory
    concatenated_dir = os.path.join(course_dir, "lichen", "concatenated", gradeable)
    if not os.path.isdir(concatenated_dir):
        os.makedirs(concatenated_dir)

    # =========================================================================
    # walk the subdirectories
    for user in sorted(os.listdir(submission_dir)):
        if not os.path.isdir(os.path.join(submission_dir, user)):
            continue
        for version in sorted(os.listdir(os.path.join(submission_dir, user))):
            if not os.path.isdir(os.path.join(submission_dir, user, version)):
                continue

            # -----------------------------------------------------------------
            # concatenate all files for this submisison into a single file
            my_concatenated_dir = os.path.join(concatenated_dir, user, version)
            if not os.path.isdir(my_concatenated_dir):
                os.makedirs(my_concatenated_dir)
            my_concatenated_file = os.path.join(my_concatenated_dir, "submission.concatenated")
            total_concat = 0
            with open(my_concatenated_file, 'w') as my_cf:
                # loop over all files in all subdirectories
                base_path = os.path.join(submission_dir, user, version)
                for my_dir, _dirs, my_files in os.walk(base_path):
                    # Determine if regex should be used
                    files = sorted(my_files)
                    if expressions is not None:
                        files_filtered = []
                        for e in expressions:
                            files_filtered.extend(fnmatch.filter(files, e.strip()))
                        files = files_filtered
                    total_concat += len(files)
                    for my_file in files:
                        # skip the timestep
                        if my_file == ".submit.timestamp":
                            continue
                        absolute_path = os.path.join(my_dir, my_file)
                        # print a separator & filename
                        with open(absolute_path, encoding='ISO-8859-1') as tmp:
                            # append the contents of the file
                            my_cf.write(tmp.read())
            # Remove concat file if there no content...
            if total_concat == 0:
                os.remove(my_concatenated_file)
                # FIXME: is this the correct path?
                p2 = os.path.join(course_dir, "lichen", "tokenized", gradeable, user, version)
                if os.path.isdir(p2):
                    shutil.rmtree(p2)
                os.rmdir(my_concatenated_dir)

    # =========================================================================
    # concatenate any files in the provided_code directory
    provided_code_path = os.path.join(course_dir, "lichen", "provided_code", gradeable)
    output_dir = os.path.join(course_dir, "lichen", "concatenated", gradeable, "provided_code")
    output_file = os.path.join(output_dir, "provided_code.concatenated")

    if os.path.isdir(provided_code_path) and len(os.listdir(provided_code_path)) != 0:
        # If the directory already exists, delete it and make a new one
        if os.path.isdir(output_dir):
            shutil.rmtree(output_dir)
        os.makedirs(output_dir)

        with open(output_file, 'w') as of:
            # Loop over all of the provided files and concatenate them
            for file in sorted(os.listdir(provided_code_path)):
                with open(os.path.join(provided_code_path, file), encoding='ISO-8859-1') as tmp:
                    # append the contents of the file
                    of.write(tmp.read())

    print("done")


if __name__ == "__main__":
    main()
