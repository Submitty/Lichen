#!/usr/bin/env python3
"""
Walks the submission directory and creates a parallel directory of
the tokenized files.

"""

import argparse
import os
import json
import subprocess
import sys
import json
import hashlib
from shutil import rmtree


CONFIG_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..', 'config')
with open(os.path.join(CONFIG_PATH, 'submitty.json')) as open_file:
    OPEN_JSON = json.load(open_file)
SUBMITTY_DATA_DIR = OPEN_JSON['submitty_data_dir']
SUBMITTY_INSTALL_DIR = OPEN_JSON['submitty_install_dir']

def parse_args():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("config_path")
    args = parser.parse_args()
    return args


def hasher(args,my_tokenized_file,my_hashes_file):
    with open(args.config_path) as lichen_config:
        lichen_config_data = json.load(lichen_config)
        language = lichen_config_data["language"]
        sequence_length = int(lichen_config_data["sequence_length"])

    data_json_path = os.path.join(SUBMITTY_INSTALL_DIR, "Lichen", "bin", "data.json")
    with open(data_json_path) as token_data_file:
        token_data = json.load(token_data_file)
        if not language in token_data:
            print("\n\nERROR: UNKNOWN HASHER\n\n")
            exit(1)

    if (sequence_length < 1):
        print ("ERROR! sequence_length must be >= 1")
        exit(1)

    with open(my_tokenized_file,'r',encoding='ISO-8859-1') as my_tf:
        with open(my_hashes_file,'w') as my_hf:
            tokens = json.load(my_tf)
            token_values = [str(x.get(token_data[language]["token_value"])) for x in tokens]
            num = len(tokens)
            #FIXME: this truncation should be adjusted after more full-scale testing
            token_hashed_values = [ (hashlib.md5(''.join(token_values[x:x+sequence_length]).encode()).hexdigest())[0:8] for x in range(0, num-sequence_length)]
            my_hf.write('\n'.join(token_hashed_values))

def main():
    args = parse_args()

    with open(args.config_path) as lichen_config:
        lichen_config_data = json.load(lichen_config)
        semester = lichen_config_data["semester"]
        course = lichen_config_data["course"]
        gradeable = lichen_config_data["gradeable"]

    sys.stdout.write("HASH ALL...")
    sys.stdout.flush()

    # ===========================================================================
    # error checking
    course_dir=os.path.join(SUBMITTY_DATA_DIR,"courses",semester,course)
    if not os.path.isdir(course_dir):
        print("ERROR! ",course_dir," is not a valid course directory")
        exit(1)
    tokenized_dir=os.path.join(course_dir,"lichen","tokenized",gradeable)
    if not os.path.isdir(tokenized_dir):
        print("ERROR! ",tokenized_dir," is not a valid gradeable tokenized directory")
        exit(1)

    hashes_dir=os.path.join(course_dir,"lichen","hashes",gradeable)
    if os.path.isdir(hashes_dir):
        rmtree(hashes_dir)
        os.mkdir(hashes_dir)

    # ===========================================================================
    # walk the subdirectories
    for user in sorted(os.listdir(tokenized_dir)):
        for version in sorted(os.listdir(os.path.join(tokenized_dir,user))):
            my_tokenized_file=os.path.join(tokenized_dir,user,version,"tokens.json")

            # ===========================================================================
            # create the directory
            my_hashes_dir=os.path.join(hashes_dir,user,version)
            if not os.path.isdir(my_hashes_dir):
                os.makedirs(my_hashes_dir)

            my_hashes_file=os.path.join(my_hashes_dir,"hashes.txt")
            hasher(args,my_tokenized_file,my_hashes_file)

    print("done")

if __name__ == "__main__":
    main()
