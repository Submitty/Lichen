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

CONFIG_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..', 'config')
with open(os.path.join(CONFIG_PATH, 'submitty.json')) as open_file:
    OPEN_JSON = json.load(open_file)
SUBMITTY_DATA_DIR = OPEN_JSON['submitty_data_dir']
SUBMITTY_INSTALL_DIR = OPEN_JSON['submitty_install_dir']


def parse_args():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("semester")
    parser.add_argument("course")
    parser.add_argument("gradeable")
    parser.add_argument("--window",type=int,default=10)
    language = parser.add_mutually_exclusive_group(required=True)
    language.add_argument ("--plaintext", action='store_true')
    language.add_argument ("--python", action='store_true')
    language.add_argument ("--cpp", action='store_true')
    return parser.parse_args()


def hasher(args,my_tokenized_file,my_hashes_file):

    with open(my_tokenized_file) as my_tf:
        tokens = json.load(my_tf)
        print("num ",len(tokens))
    
    if args.plaintext:
        print("HASH PLAINTEXT")
    elif args.python:
        print("NEED A PYTHON TOKENIZER")
    elif args.cpp:
        print("NEED A C++ TOKENIZER")
    else:
        print("UNKNOWN TOKENIZER")

        
def main():
    args = parse_args()

    sys.stdout.write("HASH ALL...")
    sys.stdout.flush()
    
    # ===========================================================================
    # error checking
    course_dir=os.path.join(SUBMITTY_DATA_DIR,"courses",args.semester,args.course)
    if not os.path.isdir(course_dir):
        print("ERROR! ",course_dir," is not a valid course directory")
        exit(1)
    tokenized_dir=os.path.join(course_dir,"Lichen","tokenized",args.gradeable) 
    if not os.path.isdir(tokenized_dir):
        print("ERROR! ",tokenized_dir," is not a valid gradeable tokenized directory")
        exit(1)

    hashes_dir=os.path.join(course_dir,"Lichen","hashes",args.gradeable)

    # ===========================================================================
    # walk the subdirectories
    for user in os.listdir(tokenized_dir):
        for version in os.listdir(os.path.join(tokenized_dir,user)):
            my_tokenized_file=os.path.join(tokenized_dir,user,version,"tokens.json")

            # ===========================================================================
            # create the directory
            my_hashes_dir=os.path.join(hashes_dir,user,version)
            if not os.path.isdir(my_hashes_dir):
                os.makedirs(my_hashes_dir)

            my_hashes_file=os.path.join(my_hashes_dir,"hashes.txt")
            hasher(args,my_tokenized_file,my_hashes_file)
                  
            
if __name__ == "__main__":
    main()
