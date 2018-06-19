#!/usr/bin/env python3
"""
Walks the submission directory and creates a parallel directory of
the concatenated files.
"""

import argparse
import os
import json
import sys

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
    return parser.parse_args()


def main():
    args = parse_args()

    sys.stdout.write("CONCATENATE ALL...")
    sys.stdout.flush()

    # ===========================================================================
    # error checking
    course_dir=os.path.join(SUBMITTY_DATA_DIR,"courses",args.semester,args.course)
    if not os.path.isdir(course_dir):
        print("ERROR! ",course_dir," is not a valid course directory")
        exit(1)
    submission_dir=os.path.join(course_dir,"submissions",args.gradeable)
    if not os.path.isdir(submission_dir):
        print("ERROR! ",submission_dir," is not a valid gradeable submissions directory")
        exit(1)

    # ===========================================================================
    # create the directory
    concatenated_dir=os.path.join(course_dir,"lichen","concatenated",args.gradeable)
    if not os.path.isdir(concatenated_dir):
         os.makedirs(concatenated_dir)

    # ===========================================================================
    # walk the subdirectories
    for user in os.listdir(submission_dir):
        if not os.path.isdir(os.path.join(submission_dir,user)):
            continue
        for version in os.listdir(os.path.join(submission_dir,user)):
            if not os.path.isdir(os.path.join(submission_dir,user,version)):
                continue

            # ---------------------------------------------------------------------
            # concatenate all files for this gradeable/user/version into a single file
            my_concatenated_dir=os.path.join(concatenated_dir,user,version)
            if not os.path.isdir(my_concatenated_dir):
                os.makedirs(my_concatenated_dir)
            my_concatenated_file=os.path.join(my_concatenated_dir,"submission.concatenated")
            with open(my_concatenated_file,'w') as my_cf:
                # print a brief header of information
                my_cf.write("SEMESTER: "+args.semester+"\n")
                my_cf.write("COURSE: "+args.course+"\n")
                my_cf.write("GRADEABLE: "+args.gradeable+"\n")
                my_cf.write("USER: "+user+"\n")
                my_cf.write("VERSION: "+version+"\n")
                # loop over all files in all subdirectories
                base_path = os.path.join(submission_dir,user,version)
                for my_dir,dirs,my_files in os.walk(base_path):
                    for my_file in sorted(my_files):
                        # skip the timestep
                        if my_file == ".submit.timestamp":
                            continue
                        # TODO: skip files that should be ignored
                        absolute_path=os.path.join(my_dir,my_file)
                        relative_path=absolute_path[len(base_path):]
                        # print a separator & filename
                        my_cf.write("----------------------------------------------------\n")
                        my_cf.write("FILE: "+relative_path+"\n\n")
                        with open(absolute_path) as tmp:
                            # append the contents of the file
                            my_cf.write(tmp.read()+"\n")

    print ("done")
                            
if __name__ == "__main__":
    main()