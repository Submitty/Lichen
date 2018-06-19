#!/bin/bash

semester=$1
course=$2
gradeable=$3
language=$4
window=$5


/usr/local/submitty/Lichen/bin/concatenate_all.py  $semester $course $gradeable 
/usr/local/submitty/Lichen/bin/tokenize_all.py     $semester $course $gradeable  --${language}
/usr/local/submitty/Lichen/bin/hash_all.py         $semester $course $gradeable  --window $window  --${language}

/usr/local/submitty/Lichen/bin/compare_hashes.out  $semester $course $gradeable  --window $window

