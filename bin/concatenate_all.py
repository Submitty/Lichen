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

IGNORED_FILES = [
    ".submit.timestamp"
]


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

        # this assumes regex is seperated by a ','
        regex_expressions = lichen_config_data["regex"].split(',')
        regex_dirs = lichen_config_data["regex_dirs"]

    # ==========================================================================
    # error checking
    course_dir = os.path.join(SUBMITTY_DATA_DIR, "courses", semester, course)
    if not os.path.isdir(course_dir):
        print("ERROR! ", course_dir, " is not a valid course directory")
        exit(1)

    for e in regex_expressions:
        # Check for backwards crawling
        if ".." in e:
            print('ERROR! Invalid path component ".." in regex')
            exit(1)

    for dir in regex_dirs:
        if dir not in ["submissions", "results", "checkout"]:
            print("ERROR! ", dir, " is not a valid input directory for Lichen")
            exit(1)

    # ==========================================================================
    # create the directory
    concatenated_dir = os.path.join(course_dir, "lichen", "concatenated", gradeable)
    if not os.path.isdir(concatenated_dir):
        os.makedirs(concatenated_dir)

    # ==========================================================================
    count_total_files = 0

    for dir in regex_dirs:
        submission_dir = os.path.join(course_dir, dir, gradeable)

        # more error checking
        if not os.path.isdir(submission_dir):
            print("ERROR! ", submission_dir, " is not a valid gradeable ", dir, " directory")
            exit(1)

        # =========================================================================
        # walk the subdirectories
        for user in sorted(os.listdir(submission_dir)):
            if not os.path.isdir(os.path.join(submission_dir, user)):
                continue
            for version in sorted(os.listdir(os.path.join(submission_dir, user))):
                if not os.path.isdir(os.path.join(submission_dir, user, version)):
                    continue

                # -----------------------------------------------------------------
                # concatenate all files for this submissison into a single file
                my_concatenated_dir = os.path.join(concatenated_dir, user, version)
                if not os.path.isdir(my_concatenated_dir):
                    os.makedirs(my_concatenated_dir)
                my_concatenated_file = os.path.join(my_concatenated_dir, "submission.concatenated")

                with open(my_concatenated_file, 'a') as my_cf:
                    # loop over all files in all subdirectories
                    base_path = os.path.join(submission_dir, user, version)
                    for my_dir, _dirs, my_files in os.walk(base_path):
                        # Determine if regex should be used (no regex provided
                        # is equivalent to selecting all files)
                        files = sorted(my_files)
                        if regex_expressions[0] != "":
                            files_filtered = []
                            for e in regex_expressions:
                                files_filtered.extend(fnmatch.filter(files, e.strip()))
                            files = files_filtered

                        for my_file in files:
                            # exclude any files we have ignored for all submissions
                            if my_file in IGNORED_FILES:
                                continue
                            absolute_path = os.path.join(my_dir, my_file)
                            # print a separator & filename
                            my_cf.write(f"=============== {my_file} ===============\n")
                            with open(absolute_path, encoding='ISO-8859-1') as tmp:
                                # append the contents of the file
                                my_cf.write(tmp.read())
                                my_cf.write("\n")
                            count_total_files += 1
    # ==========================================================================
    # iterate over all of the created submissions, checking to see if they are
    # and adding a message to the top if so (to differentiate empty files from errors in the UI)
    for user in os.listdir(concatenated_dir):
        for version in os.listdir(os.path.join(concatenated_dir, user)):
            my_concatenated_file = os.path.join(concatenated_dir,
                                                user, version, "submission.concatenated")
            with open(my_concatenated_file, "r+") as my_cf:
                if my_cf.read() == "":
                    my_cf.write("Error: No files matched provided regex in selected directories")

    # ==========================================================================
    # concatenate any files in the provided_code directory
    provided_code_path = os.path.join(course_dir, "lichen", "provided_code", gradeable)
    output_dir = os.path.join(course_dir, "lichen", "concatenated",
                              gradeable, "provided_code", "provided_code")
    output_file = os.path.join(output_dir, "submission.concatenated")

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

    # ==========================================================================
    print("done")
    print(f"{count_total_files} files concatenated")


if __name__ == "__main__":
    main()
