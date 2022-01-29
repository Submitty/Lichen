#!/usr/bin/env python3
"""
Ranks the submissions in order of plagiarism likelihood
"""

import argparse
import os
import json
import time
import math
import statistics
from pathlib import Path


# This is a helper class which is used to store, and ultimately sort, data about submissions
class Submission():
    user_id = ''
    version = 0
    percent_match = 0  # the percent of this submission which matches other submissions
    hashes_matched = 0  # the absolute number of hashes matched
    suspicious_chunk_count = 0  # the number of chunks with high numbers of matches
    chunks = []


def parse_args():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('basepath')
    return parser.parse_args()


# getChunkList is passed the path to a matches.json file and a hashes.txt file,
# as well as a chunk size, and returns a tuple of a list containing the number
# of matching hashes found in each chunk of "chunk_size" hashes and the total
# fraction of the submission which matches.
def getChunkList(matches_file, hashes_file, chunk_size):
    # determine how many hashes there are in this submission
    with open(hashes_file, 'r') as file:
        total_hashes = len([0 for _ in file])

    # If this is a blank submission, return an empty array
    if total_hashes <= 1:
        return ([], 0)

    # chunks = [0] * (math.ceil(total_hashes / chunk_size) + 1)
    chunks = [0] * total_hashes

    # it is possible that there are no matches and thus a matches.json file isn't
    # created. If this is the case, we can simply return now.
    if not os.path.isfile(matches_file):
        return (chunks, 0)

    with open(matches_file, 'r') as file:
        matches_json = json.load(file)

    prev_end_position = 0  # there can be overlap between regions so we can't double-count
    for match in matches_json:
        if match['type'] != 'match':
            continue

        for i in range(max(match['start'], prev_end_position + 1), match['end'] + 1):
            # chunks[i // chunk_size] += 1
            for j in range(i, i + chunk_size):
                if j - 1 >= len(chunks):
                    break
                chunks[j - 1] += 1

        prev_end_position = match['end']

    return (chunks, sum(chunks) / total_hashes)


def main():
    start_time = time.time()
    args = parse_args()

    print('SIMILARITY RANKING...', end='', flush=True)

    with open(os.path.join(args.basepath, "config.json")) as lichen_config:
        lichen_config_data = json.load(lichen_config)
    lichen_config_data['sensitivity'] = 1
    lichen_config_data['chunk_size'] = 200 # TODO: REMOVE ####################################################################

    users_dir = Path(args.basepath, 'users')
    if not os.path.isdir(users_dir):
        raise SystemExit('ERROR! Unable to find users directory')

    all_submissions = list()
    all_chunks = []
    max_hashes_matched = 0

    for user in sorted(os.listdir(users_dir)):
        user_dir = Path(users_dir, user)
        if not os.path.isdir(user_dir):
            continue

        for version in sorted(os.listdir(user_dir)):
            my_dir = Path(user_dir, version)
            if not os.path.isdir(my_dir):
                continue

            matches_file = Path(my_dir, 'matches.json')
            hashes_file = Path(my_dir, 'hashes.txt')
            chunks, percent_match = getChunkList(matches_file,
                                                 hashes_file,
                                                 lichen_config_data['chunk_size'])
            all_chunks.extend(chunks)

            s = Submission()
            s.user_id = user
            s.version = int(version)
            s.chunks = chunks
            s.percent_match = percent_match
            s.hashes_matched = sum(chunks)
            # We have to wait for everything to be run before calculating suspicious_chunk_count

            all_submissions.append(s)

            if s.hashes_matched > max_hashes_matched:
                max_hashes_matched = s.hashes_matched

    chunk_mean = statistics.mean(all_chunks)
    chunk_stddev = statistics.pstdev(all_chunks)

    print('mean:', chunk_mean)
    print('stddev:', chunk_stddev)

    for submission in all_submissions:
        counter = 0
        for chunk in submission.chunks:
            if counter > 0:
                counter -= 1
            elif chunk > chunk_mean + (lichen_config_data['sensitivity'] * chunk_stddev):
                submission.suspicious_chunk_count += 1
                # We don't want to double-count so we require the next chunk to
                # begin at least chunk_size locations from the current position.
                # This is necessary to prevent a plagiarized region from being
                # split between two fixed chunks, and therefore not taken into
                # account when ranking submissions.
                counter = lichen_config_data['chunk_size']

    all_submissions.sort(key=lambda s: (s.suspicious_chunk_count,
                                        0.5 * s.percent_match +
                                        0.5 * (s.hashes_matched / max_hashes_matched),
                                        s.hashes_matched,
                                        s.percent_match), reverse=True)

    for s in all_submissions:
        print(s.user_id, s.version, s.suspicious_chunk_count)

    # ==========================================================================
    end_time = time.time()
    print("done in " + "%.0f" % (end_time - start_time) + " seconds")


if __name__ == "__main__":
    main()
