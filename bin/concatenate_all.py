#!/usr/bin/env python3
"""
Walks the submission directory and creates a parallel directory of
the concatenated files.
"""

import argparse
import os
import sys
import json
import datetime
import humanize
import fnmatch
import hashlib
import mimetypes
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

            # check for MIME types which are not supported
            file_type = mimetypes.guess_type(my_file)[0]
            if file_type is not None and \
                    (file_type.endswith("/pdf") or file_type.startswith("image/")):
                continue

            absolute_path = os.path.join(my_dir, my_file)
            # print a separator & filename
            with open(absolute_path, encoding='ISO-8859-1') as tmp:
                result += f"==== {my_file} ====\n"
                # append the contents of the file
                result += tmp.read() + "\n"
    return result


# This function is passed a path to a gradeable and an output path to place files in and
# concatenates all of the files for each submission into a single file in the output directory
# returns the total size of the files concatenated
def processGradeable(basepath, config, input_dir, output_dir, total_concat):
    # basic error checking
    if not Path(input_dir).exists():
        raise SystemExit(f"ERROR: Unable to find directory {input_dir}")

    if Path(input_dir).group() != Path(basepath).group():
        raise SystemExit(f"ERROR: Group for directory {input_dir} does not"
                         f"match group for {basepath} directory")

    # loop over each user
    for user in sorted(os.listdir(input_dir)):
        user_path = os.path.join(input_dir, user)
        if not os.path.isdir(user_path):
            continue
        elif user in config["ignore_submissions"]:
            continue

        if config["version"] == "active_version":
            # get the user's active version from their settings file if it exists, else get
            # most recent version for compatibility with early versions of Submitty
            submissions_details_path = os.path.join(user_path, 'user_assignment_settings.json')
            if os.path.exists(submissions_details_path):
                with open(submissions_details_path) as details_file:
                    details_json = json.load(details_file)
                    my_active_version = int(details_json["active_version"])
            else:
                # get the most recent version
                my_active_version = sorted(os.listdir(user_path))[-1]

        # loop over each version
        for version in sorted(os.listdir(user_path)):
            version_path = os.path.join(user_path, version)
            if dir == "results":
                # only the "details" folder within "results" contains files relevant to Lichen
                version_path = os.path.join(version_path, "details")
            if not os.path.isdir(version_path):
                continue
            if config["version"] == "active_version" and int(version) != my_active_version:
                continue

            output_file_path = os.path.join(output_dir, user, version, "submission.concatenated")

            if not os.path.exists(os.path.dirname(output_file_path)):
                os.makedirs(os.path.dirname(output_file_path))

            # append to concatenated file
            with open(output_file_path, "a") as output_file:
                concatenated_contents = getConcatFilesInDir(version_path, config["regex"])
                output_file.write(concatenated_contents)
                total_concat += sys.getsizeof(concatenated_contents)

            # If we've exceeded the concatenation limit, kill program
            checkTotalSize(total_concat)
    return total_concat


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
    hash_size = int(config["hash_size"])
    other_gradeables = config["other_gradeables"]

    # Check we have a tokenizer to support the configured language
    langs_data_json_path = Path(Path(__file__).resolve().parent.parent,
                                "tokenizer", "tokenizer_config.json")
    with open(langs_data_json_path, 'r') as langs_data_file:
        langs_data = json.load(langs_data_file)
        if language not in langs_data:
            raise SystemExit(f"ERROR: tokenizing not supported for language {language}")

    # Check values of common code threshold and hash size
    if (threshold < 2):
        raise SystemExit("ERROR: threshold must be >= 2")

    if (hash_size < 1):
        raise SystemExit("ERROR: hash_size must be >= 1")

    # Check for backwards crawling
    for e in regex_patterns:
        if ".." in e:
            raise SystemExit('ERROR: Invalid path component ".." in regex')

    for gradeable in other_gradeables:
        for field in gradeable:
            if ".." in field:
                raise SystemExit('ERROR: Invalid component ".." in other_gradeable path')

    # check permissions to make sure we have access to the other gradeables
    my_course_group_perms = Path(args.basepath).group()
    for gradeable in other_gradeables:
        if Path(args.datapath, gradeable["other_semester"], gradeable["other_course"]).group()\
           != my_course_group_perms:
            raise SystemExit("ERROR: Invalid permissions to access course "
                             f"{gradeable['other_semester']}/{gradeable['other_course']}")

    # check permissions for each path we are given (if any are provided)
    if config.get("other_gradeable_paths") is not None:
        for path in config["other_gradeable_paths"]:
            if Path(path).group() != my_course_group_perms:
                raise SystemExit(f"ERROR: Group for directory {path} does not"
                                 f"match group for {args.basepath} directory")

    # make sure the regex directory is one of the acceptable directories
    for dir in regex_dirs:
        if dir not in ["submissions", "results", "checkout"]:
            raise SystemExit(f"ERROR: {dir} is not a valid input directory for Lichen")


def main():
    start_time = datetime.datetime.now()
    args = parse_args()

    print("CONCATENATE ALL:", flush=True)

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
    regex_patterns = config["regex"]
    regex_dirs = config["regex_dirs"]
    other_gradeables = config["other_gradeables"]
    # optional field -> other_gradeable_paths=None if key doesn't exist
    other_gradeable_paths = config.get("other_gradeable_paths")

    # ==========================================================================
    # loop through and concatenate the selected files for each user in this gradeable
    total_concat = 0

    for dir in regex_dirs:
        input_path = os.path.join(args.datapath, semester, course, dir, gradeable)
        output_path = os.path.join(args.basepath, "users")
        total_concat = processGradeable(args.basepath, config,
                                        input_path, output_path, total_concat)

    # ==========================================================================
    # loop over all of the other gradeables and concatenate their submissions
    for other_gradeable in other_gradeables:
        for dir in regex_dirs:
            input_path = os.path.join(args.datapath,
                                      other_gradeable["other_semester"],
                                      other_gradeable["other_course"],
                                      dir,
                                      other_gradeable["other_gradeable"])

            output_path = os.path.join(args.basepath, "other_gradeables",
                                       f"{other_gradeable['other_semester']}__{other_gradeable['other_course']}__{other_gradeable['other_gradeable']}")  # noqa: E501
            total_concat = processGradeable(args.basepath, config,
                                            input_path, output_path, total_concat)

    # take care of any manually-specified paths if they exist
    if other_gradeable_paths is not None:
        for path in other_gradeable_paths:
            # We hash the path as the name of the gradeable
            dir_name = hashlib.md5(path.encode('utf-8')).hexdigest()
            output_path = os.path.join(args.basepath, "other_gradeables", dir_name)
            total_concat = processGradeable(args.basepath, config, path,
                                            output_path, total_concat)

    # ==========================================================================
    # iterate over all of the created submissions, checking to see if they are empty
    # and printing a message if so

    empty_directories = []  # holds a list of users who had no files concatenated

    for user in os.listdir(os.path.join(args.basepath, "users")):
        user_path = os.path.join(args.basepath, "users", user)
        for version in os.listdir(user_path):
            version_path = os.path.join(user_path, version)
            my_concatenated_file = os.path.join(version_path, "submission.concatenated")
            with open(my_concatenated_file, "r") as my_cf:
                if my_cf.read() == "":
                    empty_directories.append(f"{user}:{version}")
    if len(empty_directories) > 0:
        print("Warning: No files matched provided regex in selected directories for user(s):",
              ", ".join(empty_directories))

    # do the same for the other gradeables
    for other_gradeable in os.listdir(os.path.join(args.basepath, "other_gradeables")):
        empty_directories = []
        for other_user in os.listdir(os.path.join(args.basepath,
                                                  "other_gradeables", other_gradeable)):
            other_user_path = os.path.join(args.basepath, "other_gradeables",
                                           other_gradeable, other_user)
            for other_version in os.listdir(other_user_path):
                other_version_path = os.path.join(other_user_path, other_version)
                my_concatenated_file = os.path.join(other_version_path, "submission.concatenated")
                with open(my_concatenated_file, "r") as my_cf:
                    if my_cf.read() == "":
                        empty_directories.append(f"{other_user}:{other_version}")
        if len(empty_directories) > 0:
            print("Warning: No files matched provided regex in selected directories for user(s):",
                  ", ".join(empty_directories), "in gradeable", other_gradeable)

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
    print("Concatenation done in", humanize.precisedelta(start_time, format="%1.f") + ",",
          humanize.naturalsize(total_concat), "concatenated")


if __name__ == "__main__":
    main()
