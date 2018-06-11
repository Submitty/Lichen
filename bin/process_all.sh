#!/bin/bash

semester=$1
course=$2
gradeable=$3

/usr/local/submitty/Lichen/bin/concatenate_all.py  $semester $course $gradeable 
/usr/local/submitty/Lichen/bin/tokenize_all.py     $semester $course $gradeable  --plaintext
/usr/local/submitty/Lichen/bin/hash_all.py         $semester $course $gradeable  --window 10  --plaintext

/usr/local/submitty/Lichen/bin/compare_hashes.out  $semester $course $gradeable 

