#!/usr/bin/env python3
"""
Walks the submission directory and creates a parallel directory of
the concatenated files.
"""

import argparse
import os
import json
import sys
import time
import fnmatch

IGNORED_FILES = [
    ".submit.timestamp"
]


# returns a string containing the contents of the files which match the regex in the specified dir
def getConcatFilesInDir(input_dir, regex_patterns):
    result = ""
    for my_dir, _dirs, my_files in os.walk(input_dir):
        # Determine if regex should be used (blank regex is equivalent to selecting all files)
        files = sorted(my_files)
        if regex_patterns[0] != "":
            files_filtered = []
            for e in regex_patterns:
                files_filtered.extend(fnmatch.filter(files, e.strip()))
            files = files_filtered

        for my_file in files:
            # exclude any files we have ignored for all submissions
            if my_file in IGNORED_FILES:
                continue
            absolute_path = os.path.join(my_dir, my_file)
            # print a separator & filename
            with open(absolute_path, encoding='ISO-8859-1') as tmp:
                result += f"=============== {my_file} ===============\n"
                # append the contents of the file
                result += tmp.read() + "\n"
    return result


def parse_args():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("basepath")
    parser.add_argument("datapath")
    return parser.parse_args()


def main():
    start_time = time.time()
    args = parse_args()

    sys.stdout.write("CONCATENATE ALL...")  # don't want a newline here so can't use print
    sys.stdout.flush()

    config_path = os.path.join(args.basepath, "config.json")
    if not os.path.isfile(config_path):
        print(f"Error: invalid config path provided ({config_path})")
        exit(1)

    with open(config_path) as config_file:
        config = json.load(config_file)

    semester = config["semester"]
    course = config["course"]
    gradeable = config["gradeable"]
    version_mode = config["version"]
    users_to_ignore = config["ignore_submissions"]
    regex_patterns = config["regex"].split(',')
    regex_dirs = config["regex_dirs"]

    # ==========================================================================
    # Error checking

    # Check for backwards crawling
    for e in regex_patterns:
        if ".." in e:
            print('ERROR! Invalid path component ".." in regex')
            exit(1)

    for dir in regex_dirs:
        if dir not in ["submissions", "results", "checkout"]:
            print("ERROR! ", dir, " is not a valid input directory for Lichen")
            exit(1)

    # ==========================================================================
    # loop through and concatenate the selected files for each user in this gradeable

    for dir in regex_dirs:
        gradeable_path = os.path.join(args.datapath, semester, course, dir, gradeable)
        # loop over each user
        for user in sorted(os.listdir(gradeable_path)):
            user_path = os.path.join(gradeable_path, user)
            if not os.path.isdir(user_path):
                continue
            elif user in users_to_ignore:
                continue

            my_active_version = 0
            if version_mode == "active_version":
                # get the user's active version from their settings file
                submissions_details_path = os.path.join(user_path, 'user_assignment_settings.json')
                with open(submissions_details_path) as details_file:
                    details_json = json.load(details_file)
                    my_active_version = int(details_json["active_version"])

            # loop over each version
            for version in sorted(os.listdir(user_path)):
                version_path = os.path.join(user_path, version)
                if not os.path.isdir(version_path):
                    continue
                if version_mode == "active_version" and int(version) != my_active_version:
                    continue

                output_file_path = os.path.join(args.basepath, "users", user,
                                                version, "submission.concatenated")

                if not os.path.exists(os.path.dirname(output_file_path)):
                    os.makedirs(os.path.dirname(output_file_path))

                # append to concatenated file
                with open(output_file_path, "a") as output_file:
                    concatenated_contents = getConcatFilesInDir(version_path, regex_patterns)
                    output_file.write(concatenated_contents)

    # ==========================================================================
    # iterate over all of the created submissions, checking to see if they are empty
    # and adding a message to the top if so (to differentiate empty files from errors in the UI)
    for user in os.listdir(os.path.join(args.basepath, "users")):
        user_path = os.path.join(args.basepath, "users", user)
        for version in os.listdir(user_path):
            version_path = os.path.join(user_path, version)
            my_concatenated_file = os.path.join(version_path, "submission.concatenated")
            with open(my_concatenated_file, "r+") as my_cf:
                if my_cf.read() == "":
                    my_cf.write("Error: No files matched provided regex in selected directories")

    # ==========================================================================
    # concatenate provided code
    with open(os.path.join(args.basepath, "provided_code",
                           "submission.concatenated"), "w") as file:
        provided_code_files = os.path.join(args.basepath, "provided_code", "files")
        file.write(getConcatFilesInDir(provided_code_files, regex_patterns))

    # ==========================================================================
    end_time = time.time()
    print("done in " + "%.0f" % (end_time - start_time) + " seconds")


if __name__ == "__main__":
    main()
