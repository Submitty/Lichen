#!/bin/sh

# This script is the startup script for Lichen.  It accepts a single path to a
# directory containing a config file and creates the necessary output directories
# as appropriate, relative to the provided path.  It is possible to run this script
# from the command line but it is meant to be run via the Plagiarism Detection UI.

# TODO: Assert permissions, as necessary

if [ "$#" -ne 2 ] || ! [ -d "$1" ] || ! [ -d "$2" ]; then
  echo "Usage: $0 <basepath> <datapath>" >&2
  exit 1
fi

BASEPATH="$1" # holds the path to a directory containing a config for this gradeable
              # (probably .../lichen/gradeable/<unique number>/ on Submitty)

DATAPATH="$2" # holds the path to a directory conatining courses and their data
              # (probably /var/local/submitty/courses on Submitty)

LICHEN_INSTALLATION_DIR=/usr/local/submitty/Lichen

# kill the script if there is no config file
if [ ! -f "${BASEPATH}/config.json" ]; then
    echo "Unable to find config.json in provided directory"
		exit 1
fi


# delete any previous run results
# TODO: determine if any caching should occur
rm -rf "${BASEPATH}/logs"
rm -rf "${BASEPATH}/other_gradeables"
rm -rf "${BASEPATH}/users"
rm -f "${BASEPATH}/overall_ranking.txt"
rm -f "${BASEPATH}/provided_code/submission.concatenated"
rm -f "${BASEPATH}/provided_code/tokens.json"
rm -f "${BASEPATH}/provided_code/hashes.txt"

# Make a logs directory so we can start logging any errors
mkdir -p "${BASEPATH}/logs"

# Run Lichen and exit if an error occurs
{
    # Create these directories if they don't already exist
    mkdir -p "${BASEPATH}/provided_code"
    [ -d "${BASEPATH}/provided_code/files" ] || {
      # If PHP hasn't created a files directory already, create one and set the permissions
      # to allow PHP to edit files here in the future
      mkdir "${BASEPATH}/provided_code/files"
      chmod g+wx "${BASEPATH}/provided_code/files" || exit 1
    }
    mkdir -p "${BASEPATH}/other_gradeables"
    mkdir -p "${BASEPATH}/users"

    ############################################################################
    # Finish setting up Lichen run

    cd "$(dirname "${0}")" || exit 1

    ############################################################################
    # Do some preprocessing
    echo "Beginning Lichen run: $(date +"%Y-%m-%d %H:%M:%S")"
    python3 concatenate_all.py "$BASEPATH" "$DATAPATH" || exit 1

    ############################################################################
    # Run Lichen

    docker run --rm -v "${BASEPATH}":/data -v "${LICHEN_INSTALLATION_DIR}":/Lichen submitty/lichen

    ############################################################################
    echo "Lichen run complete: $(date +"%Y-%m-%d %H:%M:%S")"
} >> "${BASEPATH}/logs/lichen_job_output.txt" 2>&1
