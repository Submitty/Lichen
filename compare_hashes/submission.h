#ifndef SUBMISSION_H
#define SUBMISSION_H

#include <string>
#include <unordered_map>
#include <map>
#include <unordered_set>
#include <set>
#include <vector>

#include "hash_location.h"

typedef int location_in_submission;
typedef std::string hash;

// represents a unique student-version pair, all its
// hashes, and other submissions with those hashes
class Submission {
public:
  // CONSTRUCTOR
  Submission(const std::string &s, int v) : student_(s), version_(v) {}

  // GETTERS
  const std::string & student() const { return student_; }
  int version() const { return version_; }

  const std::map<location_in_submission, std::set<HashLocation> >& getSuspiciousMatches() const {
    return suspicious_matches;
  }
  const std::set<location_in_submission>& getCommonMatches() const { return common_matches; }
  const std::set<location_in_submission>& getProvidedMatches() const { return provided_matches; }
  const std::unordered_map<std::string, std::unordered_map<std::string, std::unordered_map<int, std::unordered_set<hash>>>>& getStudentsMatched() const {
    return students_matched;
  }
  float getPercentage() const {
    return (100.0 * (suspicious_matches.size())) / hashes.size();
  }

  // MODIFIERS
  void addHash(const hash &h, location_in_submission l) { hashes.push_back(make_pair(h, l)); }
  const std::vector<std::pair<hash, location_in_submission>> & getHashes() const { return hashes; }

  void addSuspiciousMatch(location_in_submission location, const HashLocation &matching_location, hash matched_hash) {
    // save the found match
    suspicious_matches[location].insert(matching_location);
    // update the students_matched container
    students_matched[matching_location.source_gradeable][matching_location.student][matching_location.version].insert(matched_hash);
  }

  void addCommonMatch(location_in_submission location) { common_matches.insert(location); }
  void addProvidedMatch(location_in_submission location) { provided_matches.insert(location); }

private:
  std::string student_;
  int version_;
  std::vector<std::pair<hash, location_in_submission> > hashes;
  std::map<location_in_submission, std::set<HashLocation> > suspicious_matches;
  std::set<location_in_submission> common_matches;
  std::set<location_in_submission> provided_matches;

  // a container to keep track of all the students this submission
  // matched and the number of matching hashes per submission
  // <source_gradeable, <username, <version, <hashes>> > >
  std::unordered_map<std::string, std::unordered_map<std::string, std::unordered_map<int, std::unordered_set<hash>>>> students_matched;
};

#endif
