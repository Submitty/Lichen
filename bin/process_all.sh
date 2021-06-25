# This script is the startup script for Lichen.  It accepts a single path to a
# directory containing a config file and creates the necessary output directories
# as appropriate, relative to the provided path.  It is possible to run this script
# from the command line but it is meant to be run via the Plagiarism Detection UI.

# TODO: Assert permissions, as necessary

basepath=$1 # holds the path to a directory containing a config for this gradeable

# kill the script if there is no config file
if [! -f "${basepath}/config.json" ]; then
    echo "Unable to find config.json in provided directory"
		exit 1
fi

# provided_code should already exist if the user wishes to run with provided code
mkdir -p "${basepath}/logs"
mkdir -p "${basepath}/other_gradeables"
mkdir -p "${basepath}/users"


/usr/local/submitty/Lichen/bin/concatenate_all.py  $basepath
#/usr/local/submitty/Lichen/bin/tokenize_all.py     $basepath
#/usr/local/submitty/Lichen/bin/hash_all.py         $basepath
#/usr/local/submitty/Lichen/bin/compare_hashes.out  $basepath
