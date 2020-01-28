#!/bin/bash

semester=$1
course=$2
gradeable=$3

prev_argument=""
prior_term_gradeables=()
ignore_submissions=()
for argument in "$@"
do
	if [[ $argument == --* ]]
	then
		prev_argument=$argument
	else
	    case $prev_argument in
		"--language")
			language=$argument
		  	;;
		"--window")
		  	window=$argument
		  	;;
		"--threshold")
		  	threshold=$argument
		  	;;
		"--regrex")
		  	regrex=$argument
		  	;;
		"--provided_code_path")
		  	provided_code_path=$argument
		  	;;
		"--prior_term_gradeables")
			prior_term_gradeables+=("$argument")
		  	;;
		"--ignore_submissions")
			ignore_submissions+=("$argument")
		  	;;
		esac
	fi
done

/usr/local/submitty/Lichen/bin/concatenate_all.py  $semester $course $gradeable
/usr/local/submitty/Lichen/bin/tokenize_all.py     $semester $course $gradeable  --${language}
/usr/local/submitty/Lichen/bin/hash_all.py         $semester $course $gradeable  --window $window  --${language}

/usr/local/submitty/Lichen/bin/compare_hashes.out  $semester $course $gradeable  --window $window

