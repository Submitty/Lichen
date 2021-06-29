# This script is the startup script for Lichen.  It accepts a single path to a
# directory containing a config file and creates the necessary output directories
# as appropriate, relative to the provided path.  It is possible to run this script
# from the command line but it is meant to be run via the Plagiarism Detection UI.

# TODO: Assert permissions, as necessary

basepath=$1 # holds the path to a directory containing a config for this gradeable
            # (probably .../lichen/gradeable/<unique number>/ on Submitty)

datapath=$2 # holds the path to a directory conatining courses and their data
            # (probably /var/local/submitty/courses on Submitty)

# kill the script if there is no config file
if [ ! -f "${basepath}/config.json" ]; then
    echo "Unable to find config.json in provided directory"
		exit 1
fi

# delete any previous run results
# TODO: determine if any caching should occur
rm -rf "${basepath}/logs"
rm -rf "${basepath}/other_gradeables"
rm -rf "${basepath}/users"

# create these directories if they don't already exist
mkdir -p "${basepath}/logs"
mkdir -p "${basepath}/provided_code"
mkdir -p "${basepath}/provided_code/files"
mkdir -p "${basepath}/other_gradeables"
mkdir -p "${basepath}/users"

# run all of the modules and exit if an error occurs
./concatenate_all.py  $basepath $datapath || exit 1
./tokenize_all.py     $basepath || exit 1
./hash_all.py         $basepath || exit 1
./compare_hashes.out  $basepath || exit 1
