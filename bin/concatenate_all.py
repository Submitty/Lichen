#!/usr/bin/env python3
"""
Walks the submission directory and creates a parallel directory of
the concatenated files.
"""

import argparse
import os
import sys
import json
import time
import humanize
import fnmatch
from pathlib import Path

IGNORED_FILES = [
    ".submit.timestamp",
    ".user_assignment_access.json"
]

with open(Path(__file__).resolve().parent / "lichen_config.json") as lichen_config_file:
    LICHEN_CONFIG = json.load(lichen_config_file)


# returns a string containing the contents of the files which match the regex in the specified dir
def getConcatFilesInDir(input_dir, regex_patterns):
    result = ""
    for my_dir, _dirs, my_files in os.walk(input_dir):
        # Determine if regex should be used (blank regex is equivalent to selecting all files)
        files = sorted(my_files)
        if regex_patterns[0] != "":
            files_filtered = []
            # resolve all of the additions
            for e in regex_patterns:
                # Regex patterns starting with a ! indicate that files should be excluded
                if not e.strip().startswith("!"):
                    files_filtered.extend(fnmatch.filter(files, e.strip()))

            # resolve the subtractions
            for e in regex_patterns:
                if e.strip().startswith("!"):
                    files_filtered = [file for file in files_filtered if file not in
                                      fnmatch.filter(files_filtered, e.strip().replace("!", ""))]

            files = files_filtered

        for my_file in files:
            # exclude any files we have ignored for all submissions
            if my_file in IGNORED_FILES:
                continue
            absolute_path = os.path.join(my_dir, my_file)
            # print a separator & filename
            with open(absolute_path, encoding='ISO-8859-1') as tmp:
                result += f"==== {my_file} ====\n"
                # append the contents of the file
                result += tmp.read() + "\n"
    return result


def checkTotalSize(total_concat):
    if total_concat > LICHEN_CONFIG['concat_max_total_bytes']:
        raise SystemExit("ERROR! exceeded"
                         f"{humanize.naturalsize(LICHEN_CONFIG['concat_max_total_bytes'])}"
                         " of concatenated files allowed")


def parse_args():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("basepath")
    parser.add_argument("datapath")
    return parser.parse_args()


def validate(config, args):
    # load parameters from the config to be checked
    regex_patterns = config["regex"]
    regex_dirs = config["regex_dirs"]
    language = config["language"]
    threshold = int(config["threshold"])
    sequence_length = int(config["sequence_length"])
    prior_term_gradeables = config["prior_term_gradeables"]

    # Check we have a tokenizer to support the configured language
    langs_data_json_path = "./data.json"  # data.json is in the Lichen/bin directory after install
    with open(langs_data_json_path, 'r') as langs_data_file:
        langs_data = json.load(langs_data_file)
        if language not in langs_data:
            raise SystemExit(f"ERROR! tokenizing not supported for language {language}")

    # Check values of common code threshold and sequence length
    if (threshold < 2):
        raise SystemExit("ERROR! threshold must be >= 2")

    if (sequence_length < 1):
        raise SystemExit("ERROR! sequence_length must be >= 1")

    # Check for backwards crawling
    for e in regex_patterns:
        if ".." in e:
            raise SystemExit('ERROR! Invalid path component ".." in regex')

    for ptg in prior_term_gradeables:
        for field in ptg:
            if ".." in field:
                raise SystemExit('ERROR! Invalid component ".." in prior_term_gradeable path')

    # check permissions to make sure we have access to the prior term gradeables
    my_course_group_perms = Path(args.basepath).group()
    for ptg in prior_term_gradeables:
        if Path(args.datapath, ptg["prior_semester"], ptg["prior_course"]).group()\
           != my_course_group_perms:
            raise SystemExit(f"ERROR! Invalid permissions to access course {ptg['prior_semester']}"
                  f"/{ptg['prior_course']}")

    # make sure the regex directory is one of the acceptable directories
    for dir in regex_dirs:
        if dir not in ["submissions", "results", "checkout"]:
            raise SystemExit("ERROR! ", dir, " is not a valid input directory for Lichen")


def main():
    start_time = time.time()
    args = parse_args()

    print("CONCATENATE ALL...", end="")

    config_path = os.path.join(args.basepath, "config.json")
    if not os.path.isfile(config_path):
        raise SystemExit(f"ERROR! invalid config path provided ({config_path})")

    with open(config_path) as config_file:
        config = json.load(config_file)

    # perform error checking on config parameters
    validate(config, args)

    # parameters to be used in this file
    semester = config["semester"]
    course = config["course"]
    gradeable = config["gradeable"]
    version_mode = config["version"]
    regex_patterns = config["regex"]
    regex_dirs = config["regex_dirs"]
    prior_term_gradeables = config["prior_term_gradeables"]
    users_to_ignore = config["ignore_submissions"]

    # ==========================================================================
    # loop through and concatenate the selected files for each user in this gradeable
    total_concat = 0

    for dir in regex_dirs:
        gradeable_path = os.path.join(args.datapath, semester, course, dir, gradeable)
        # loop over each user
        for user in sorted(os.listdir(gradeable_path)):
            user_path = os.path.join(gradeable_path, user)
            if not os.path.isdir(user_path):
                continue
            elif user in users_to_ignore:
                continue

            if version_mode == "active_version":
                # get the user's active version from their settings file
                submissions_details_path = os.path.join(user_path, 'user_assignment_settings.json')
                with open(submissions_details_path) as details_file:
                    details_json = json.load(details_file)
                    my_active_version = int(details_json["active_version"])

            # loop over each version
            for version in sorted(os.listdir(user_path)):
                version_path = os.path.join(user_path, version)
                if dir == "results":
                    # only the "details" folder within "results" contains files relevant to Lichen
                    version_path = os.path.join(version_path, "details")
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
                    total_concat += sys.getsizeof(concatenated_contents)

                checkTotalSize(total_concat)

    # ==========================================================================
    # loop over all of the other prior term gradeables and concatenate their submissions
    for other_gradeable in prior_term_gradeables:
        for dir in regex_dirs:
            other_gradeable_path = os.path.join(args.datapath,
                                                other_gradeable["prior_semester"],
                                                other_gradeable["prior_course"],
                                                dir,
                                                other_gradeable["prior_gradeable"])
            # loop over each user
            for other_user in sorted(os.listdir(other_gradeable_path)):
                other_user_path = os.path.join(other_gradeable_path, other_user)
                if not os.path.isdir(other_user_path):
                    continue

                if version_mode == "active_version":
                    # get the user's active version from their settings file
                    other_submissions_details_path = os.path.join(other_user_path,
                                                                  'user_assignment_settings.json')

                    with open(other_submissions_details_path) as other_details_file:
                        other_details_json = json.load(other_details_file)
                        my_active_version = int(other_details_json["active_version"])

                # loop over each version
                for other_version in sorted(os.listdir(other_user_path)):
                    other_version_path = os.path.join(other_user_path, other_version)
                    if dir == "results":
                        # only the "details" folder within "results" contains files relevant to Lichen
                        other_version_path = os.path.join(other_version_path, "details")
                    if not os.path.isdir(other_version_path):
                        continue

                    other_output_file_path = os.path.join(args.basepath, "other_gradeables",
                                                          f"{other_gradeable['prior_semester']}__{other_gradeable['prior_course']}__{other_gradeable['prior_gradeable']}",  # noqa: E501
                                                          other_user, other_version,
                                                          "submission.concatenated")

                    if not os.path.exists(os.path.dirname(other_output_file_path)):
                        os.makedirs(os.path.dirname(other_output_file_path))

                    # append to concatenated file
                    with open(other_output_file_path, "a") as other_output_file:
                        other_concatenated_contents = getConcatFilesInDir(other_version_path,
                                                                          regex_patterns)
                        other_output_file.write(other_concatenated_contents)
                        total_concat += sys.getsizeof(other_concatenated_contents)

                    checkTotalSize(total_concat)

    # ==========================================================================
    # iterate over all of the created submissions, checking to see if they are empty
    # and printing a message if so

    for user in os.listdir(os.path.join(args.basepath, "users")):
        user_path = os.path.join(args.basepath, "users", user)
        for version in os.listdir(user_path):
            version_path = os.path.join(user_path, version)
            my_concatenated_file = os.path.join(version_path, "submission.concatenated")
            with open(my_concatenated_file, "r") as my_cf:
                if my_cf.read() == "":
                    print("Warning: No files matched provided regex in selected directories "
                          f"for user {user} version {version}")

    # do the same for the other gradeables
    for other_gradeable in prior_term_gradeables:
        other_gradeable_dir_name = f"{other_gradeable['prior_semester']}__{other_gradeable['prior_course']}__{other_gradeable['prior_gradeable']}"  # noqa: E501
        for other_user in os.listdir(os.path.join(args.basepath, "other_gradeables",
                                                  other_gradeable_dir_name)):
            other_user_path = os.path.join(args.basepath, "other_gradeables",
                                           other_gradeable_dir_name, other_user)
            for other_version in os.listdir(other_user_path):
                other_version_path = os.path.join(other_user_path, other_version)
                my_concatenated_file = os.path.join(other_version_path, "submission.concatenated")
                with open(my_concatenated_file, "r") as my_cf:
                    if my_cf.read() == "":
                        print("Warning: No files matched provided regex in selected directories "
                              f"for user {other_user} version {other_version}")

    # ==========================================================================
    # concatenate provided code
    with open(os.path.join(args.basepath, "provided_code",
                           "submission.concatenated"), "w") as file:
        provided_code_files = os.path.join(args.basepath, "provided_code", "files")
        provided_concatenated_files = getConcatFilesInDir(provided_code_files, regex_patterns)
        file.write(provided_concatenated_files)
        total_concat += sys.getsizeof(provided_concatenated_files)
    checkTotalSize(total_concat)

    # ==========================================================================
    end_time = time.time()
    print("done in " + "%.0f" % (end_time - start_time) + " seconds,",
          humanize.naturalsize(total_concat) + " concatenated")


if __name__ == "__main__":
    main()
