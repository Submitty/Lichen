#include <map>
#include <set>
#include <vector>

#include "hash_location.h"
#include "submission.h"

typedef int location_in_submission;
typedef unsigned int hash;
typedef std::string user_id;
typedef unsigned int version_number;

void Submission::addSuspiciousMatch(location_in_submission location, const HashLocation &matching_location, const hash &matched_hash) {
  // figure out if there is an overlap between this hash and a common/provided match
  int hash_size = config_.hash_size;
  for (int i = location - 1; i > location - hash_size && i >= 0; i--) {
    if (common_matches.find(i) != common_matches.end() || provided_matches.find(i) != provided_matches.end()) {
      return;
    }
  }

  // save the found match
  suspicious_matches[location].insert(matching_location);
  // update the students_matched container
  students_matched[matching_location.source_gradeable][matching_location.student][matching_location.version].insert(matched_hash);
}

void Submission::addCommonMatch(location_in_submission location) {
  // figure out if there is an overlap between this hash and a match
  int hash_size = config_.hash_size;
  for (int i = location - 1; i > location - hash_size && i >= 0; i--) {
    std::map<location_in_submission, std::set<HashLocation> >::const_iterator find_i = suspicious_matches.find(i);
    // if there is an overlap, remove the suspicious match that overlaps
    // hopefully this doesn't cause problems with other submissions thinking
    // this hash still matches...
    if (find_i != suspicious_matches.end()) {
      suspicious_matches.erase(find_i);
    }
  }

  common_matches.insert(location);
}

void Submission::addProvidedMatch(location_in_submission location) {
  // figure out if there is an overlap between this hash and a match
  int hash_size = config_.hash_size;
  for (int i = location - 1; i > location - hash_size && i >= 0; i--) {
    std::map<location_in_submission, std::set<HashLocation> >::const_iterator find_i = suspicious_matches.find(i);
    // if there is an overlap, remove the suspicious match that overlaps
    // hopefully this doesn't cause problems with other submissions thinking
    // this hash still matches...
    if (find_i != suspicious_matches.end()) {
      suspicious_matches.erase(find_i);
    }
  }

  provided_matches.insert(location);
}
