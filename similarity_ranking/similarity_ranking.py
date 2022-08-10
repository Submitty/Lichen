#!/usr/bin/env python3
"""
Ranks the submissions in order of plagiarism likelihood
"""

import argparse
import os
import json
import humanize
import datetime
from pathlib import Path


# This is a helper class which is used to store, and ultimately sort, data about submissions
class Submission:
    def __init__(self, user_id, version):
        self.user_id = user_id
        self.version = version

        # The percent of this submission which matches other submissions
        self.percent_match = 0

        # The absolute number of hashes matched
        self.total_hashes_matched = 0

        # The highest number of matches between this user and any other single submission
        self.highest_match_count = 0

    # We use this for sorting submissions later on.  Future adjustments to the
    # ranking algorithm should modify this function.
    def __lt__(self, other):
        return self.highest_match_count < other.highest_match_count


class Match:
    def __init__(self, user_id, version, source_gradeable):
        self.user_id = user_id
        self.version = version
        self.source_gradeable = source_gradeable

        # The number of hashes this match shares with a Submission
        self.matching_hash_count = 0


def parse_args():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('basepath')
    return parser.parse_args()


# get_submission_stats is passed a user, version, a path to a matches.json, a
# path to a hashes.txt file, and the hash size and returns a pair of a Submission()
# object conatining a number of statistics about the specified submission, and a
# list of Match objects which match this submission
def get_submission_stats(user_id, version, matches_file, hashes_file, hash_size):
    submission = Submission(user_id, version)

    # Determine how many hashes there are in this submission
    with open(hashes_file, 'r') as file:
        token_count = len([0 for _ in file]) + hash_size

    # If this is a blank/empty submission, return now
    if token_count <= 1:
        return submission, []

    # It is possible that there are no matches and thus a matches.json file isn't
    # created. If this is the case, we can simply return now.
    if not os.path.isfile(matches_file):
        return submission, []

    with open(matches_file, 'r') as file:
        matches_json = json.load(file)

    # Calculate the total number of hashes matched, as well as the number of
    # hashes matched for every other submission with matches
    matching_submissions = dict()
    prev_end = 0
    for match in matches_json:
        # Common and provided code doesn't have an others list (due to size contraints)
        if match['type'] != 'match':
            continue

        for other in match['others']:
            other_submission = f"{other['username']}_{other['version']}_{other['source_gradeable']}"  # noqa: E501
            if other_submission not in matching_submissions.keys():
                matching_submissions[other_submission] = Match(other['username'],
                                                               other['version'],
                                                               other['source_gradeable'])
            matching_submissions[other_submission].matching_hash_count += \
                match['end'] - max(prev_end, match['start'] - 1)
        submission.total_hashes_matched += match['end'] - max(prev_end, match['start'] - 1)
        prev_end = match['end']

    # Actually stored as the fraction of the submission which matches
    submission.percent_match = submission.total_hashes_matched / token_count

    if len(matching_submissions.values()) > 0:
        matching_submissions = list(matching_submissions.values())

        matching_submissions.sort(key=lambda x: x.matching_hash_count, reverse=True)
        submission.highest_match_count = matching_submissions[0].matching_hash_count
    else:
        matching_submissions = []

    return submission, matching_submissions


def main():
    start_time = datetime.datetime.now()
    args = parse_args()

    print("SIMILARITY RANKING:", flush=True)
    print("[0%                      25%                     50%                     75%                     100%]\n[", end="", flush=True)  # noqa: E501

    with open(Path(args.basepath, "config.json")) as lichen_config_file:
        lichen_config = json.load(lichen_config_file)

    users_dir = Path(args.basepath, 'users')
    if not os.path.isdir(users_dir):
        raise SystemExit('ERROR! Unable to find users directory')

    # We'll make a rough estimate of the percentage of ranking output done by
    # taking the percentage of users which have been done thus far
    total_users = len(os.listdir(users_dir))
    users_ranking_output = 0
    percent_progress = 0

    all_submissions = list()

    for user in sorted(os.listdir(users_dir)):
        user_dir = Path(users_dir, user)
        if not os.path.isdir(user_dir):
            continue

        for version in sorted(os.listdir(user_dir)):
            version_dir = Path(user_dir, version)
            if not os.path.isdir(version_dir):
                continue

            matches_file = Path(version_dir, 'matches.json')
            hashes_file = Path(version_dir, 'hashes.txt')

            submission, matching_submissions = get_submission_stats(user,
                                                                    version,
                                                                    matches_file,
                                                                    hashes_file,
                                                                    lichen_config['hash_size'])
            all_submissions.append(submission)

            # Write the ranking.txt for this submission
            with open(Path(version_dir, 'ranking.txt'), 'w') as ranking_file:
                # matching_submissions is already sorted by the absolute number of hashes matched
                for match in matching_submissions:
                    ranking_file.write(f"{match.user_id:10} {match.version:3} "
                                       f"{match.source_gradeable} {match.matching_hash_count:>8}\n")

        users_ranking_output += 1
        if int((users_ranking_output / total_users) * 100) > percent_progress:
            new_percent_progress = int((users_ranking_output / total_users) * 100)
            print("|" * (new_percent_progress - percent_progress), end="", flush=True)
            percent_progress = new_percent_progress

    all_submissions.sort(reverse=True)

    # A set of all the users we've written lines for thus far (duplicates aren't allowed)
    users_written = set()
    with open(Path(args.basepath, 'overall_ranking.txt'), 'w') as ranking_file:
        for s in all_submissions:
            if s.user_id in users_written or s.total_hashes_matched == 0:
                continue
            ranking_file.write(f"{s.user_id:10} {s.version:3} "
                               f"{s.percent_match:4.0%} {s.total_hashes_matched:>8}\n")
            users_written.add(s.user_id)

    # ==========================================================================
    print("]\nSimilarity ranking done in", humanize.precisedelta(start_time, format="%1.f"))


if __name__ == "__main__":
    main()
