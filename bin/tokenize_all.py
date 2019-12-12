#!/usr/bin/env python3
"""
Tokenizes the concatenated files.
"""

import argparse
import os
import json
import subprocess
import sys


CONFIG_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..', 'config')
with open(os.path.join(CONFIG_PATH, 'submitty.json')) as open_file:
    OPEN_JSON = json.load(open_file)
SUBMITTY_DATA_DIR = OPEN_JSON['submitty_data_dir']
SUBMITTY_INSTALL_DIR = OPEN_JSON['submitty_install_dir']


def parse_args():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("config_path")
    return parser.parse_args()

def tokenize(args,my_concatenated_file,my_tokenized_file):

    with open(args.config_path) as lichen_config:
        lichen_config_data = json.load(lichen_config)
        language = lichen_config_data["language"]

    if language == "plaintext":
        tokenizer = os.path.join(SUBMITTY_INSTALL_DIR,"Lichen","bin","plaintext_tokenizer.out")
        with open(my_concatenated_file,'r') as infile:
            with open (my_tokenized_file,'w') as outfile:
                subprocess.call([tokenizer,"--ignore_newlines"],stdin=infile,stdout=outfile)

    elif language == "python":
        tokenizer = os.path.join(SUBMITTY_INSTALL_DIR,"Lichen","bin","python_tokenizer.py")
        with open(my_concatenated_file,'r') as infile:
            with open (my_tokenized_file,'w') as outfile:
                command="python3 "+str(tokenizer)+" "+my_concatenated_file+" > "+my_tokenized_file
                os.system(command)

    elif language == "cpp":
        tokenizer = os.path.join(SUBMITTY_INSTALL_DIR,"Lichen","bin","c_tokenizer.py")
        with open(my_concatenated_file,'r') as infile:
            with open (my_tokenized_file,'w') as outfile:
                command="python "+str(tokenizer)+" "+my_concatenated_file+" > "+my_tokenized_file
                os.system(command)

    elif language == "java":
        tokenizer = os.path.join(SUBMITTY_INSTALL_DIR,"Lichen","bin","java_tokenizer.py")
        with open(my_concatenated_file,'r') as infile:
            with open (my_tokenized_file,'w') as outfile:
                command="python "+str(tokenizer)+" "+my_concatenated_file+" > "+my_tokenized_file
                os.system(command)

    elif language == "mips":
        tokenizer = os.path.join(SUBMITTY_INSTALL_DIR,"Lichen","bin","mips_tokenizer.py")
        with open(my_concatenated_file,'r') as infile:
            with open (my_tokenized_file,'w') as outfile:
                command="python3 "+str(tokenizer)+" "+my_concatenated_file+" > "+my_tokenized_file
                os.system(command)

    else:
        print("\n\nERROR: UNKNOWN TOKENIZER\n\n")
        exit(1)


def main():
    args = parse_args()

    sys.stdout.write("TOKENIZE ALL...")
    sys.stdout.flush()
    
    with open(args.config_path) as lichen_config:
        lichen_config_data = json.load(lichen_config)
        semester = lichen_config_data["semester"]
        course = lichen_config_data["course"]
        gradeable = lichen_config_data["gradeable"]

    # ===========================================================================
    # error checking
    course_dir=os.path.join(SUBMITTY_DATA_DIR,"courses",semester,course)
    if not os.path.isdir(course_dir):
        print("ERROR! ",course_dir," is not a valid course directory")
        exit(1)
    concatenated_dir=os.path.join(course_dir,"lichen","concatenated",gradeable)
    if not os.path.isdir(concatenated_dir):
        print("ERROR! ",concatenated_dir," is not a valid gradeable concatenated directory")
        exit(1)

    tokenized_dir=os.path.join(course_dir,"lichen","tokenized",gradeable)

    # ===========================================================================
    # walk the subdirectories
    for user in sorted(os.listdir(concatenated_dir)):
        for version in sorted(os.listdir(os.path.join(concatenated_dir,user))):
            my_concatenated_file=os.path.join(concatenated_dir,user,version,"submission.concatenated")

            # ===========================================================================
            # create the directory
            my_tokenized_dir=os.path.join(tokenized_dir,user,version)
            if not os.path.isdir(my_tokenized_dir):
                os.makedirs(my_tokenized_dir)
            my_tokenized_file=os.path.join(my_tokenized_dir,"tokens.json")
            tokenize(args,my_concatenated_file,my_tokenized_file)

    print ("done")

    
if __name__ == "__main__":
    main()
