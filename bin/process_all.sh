#!/bin/sh

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
rm -f "${basepath}/overall_ranking.txt"
rm -f "${basepath}/provided_code/submission.concatenated"
rm -f "${basepath}/provided_code/tokens.json"
rm -f "${basepath}/provided_code/hashes.txt"

# create these directories if they don't already exist
mkdir -p "${basepath}/logs"
mkdir -p "${basepath}/provided_code"
mkdir -p "${basepath}/provided_code/files"
mkdir -p "${basepath}/other_gradeables"
mkdir -p "${basepath}/users"

# Run Lichen and exit if an error occurs
{
    ############################################################################
    # Finish setting up Lichen run

    # The default is r-x and we need PHP to be able to write if edits are made to the provided code
    chmod g=rwxs "${basepath}/provided_code/files" || exit 1

    cd "$(dirname "${0}")" || exit 1

    ############################################################################
    # Do some preprocessing
    echo "Beginning Lichen run: $(date +"%Y-%m-%d %H:%M:%S")"
    ./concatenate_all.py "$basepath" "$datapath" || exit 1

    ############################################################################
    # Move the file somewhere to be processed (eventually this will be a worker machine)

    # Tar+zip the file structure and save it to /tmp
    cd $basepath || exit 1
    archive_name=$(sha1sum "${basepath}/config.json" | awk '{ print $1 }') || exit 1
    tar -czf "/tmp/LICHEN_JOB_${archive_name}.tar.gz" "config.json" "other_gradeables" "users" "provided_code" || exit 1
    cd "$(dirname "${0}")" || exit 1

    # TODO: move the archive to worker machine for processing

    # Extract archive
    tmp_location="/tmp/LICHEN_JOB_${archive_name}"
    mkdir $tmp_location || exit 1
    tar -xzf "/tmp/LICHEN_JOB_${archive_name}.tar.gz" -C "$tmp_location"
    rm "/tmp/LICHEN_JOB_${archive_name}.tar.gz" || exit 1

    ############################################################################
    # Run Lichen
    ./tokenize_all.py    "$tmp_location" || { rm -rf $tmp_location; rm "/tmp/LICHEN_JOB_${archive_name}.tar.gz"; exit 1; }
    ./hash_all.py        "$tmp_location" || { rm -rf $tmp_location; rm "/tmp/LICHEN_JOB_${archive_name}.tar.gz"; exit 1; }
    ./compare_hashes.out "$tmp_location" || { rm -rf $tmp_location; rm "/tmp/LICHEN_JOB_${archive_name}.tar.gz"; exit 1; }

    ############################################################################
    # Zip the results back up and send them back to the course's lichen directory
    cd $tmp_location || exit 1
    tar -czf "/tmp/LICHEN_JOB_${archive_name}.tar.gz" "."
    rm -rf $tmp_location || exit 1

    # TODO: Move the archive back from worker machine

    # Extract archive and restore Lichen file structure
    cd $basepath || exit 1
    tar --skip-old-files -xzf "/tmp/LICHEN_JOB_${archive_name}.tar.gz" -C "$basepath"
    rm "/tmp/LICHEN_JOB_${archive_name}.tar.gz" || exit 1

} >> "${basepath}/logs/lichen_job_output.txt" 2>&1
