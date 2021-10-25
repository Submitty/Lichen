#ifndef SUBMISSION_H
#define SUBMISSION_H

#include <string>
#include <unordered_map>
#include <map>
#include <unordered_set>
#include <set>
#include <vector>

#include "hash_location.h"
#include "lichen_config.h"

typedef int location_in_submission;
typedef unsigned int hash;
typedef std::string user_id;
typedef unsigned int version_number;

// represents a unique student-version pair, all its
// hashes, and other submissions with those hashes
class Submission {
public:
  // CONSTRUCTOR
  Submission(const user_id &s, version_number v, const LichenConfig &c) : student_(s), version_(v), config_(c) {}

  // GETTERS
  const user_id& student() const { return student_; }
  version_number version() const { return version_; }

  const std::map<location_in_submission, std::set<HashLocation> >& getSuspiciousMatches() const { return suspicious_matches; }
  const std::set<location_in_submission>& getCommonMatches() const { return common_matches; }
  const std::set<location_in_submission>& getProvidedMatches() const { return provided_matches; }
  const std::unordered_map<std::string, std::unordered_map<user_id, std::unordered_map<version_number, std::unordered_set<hash>>>>& getStudentsMatched() const { return students_matched; }
  const std::vector<std::pair<hash, location_in_submission>> & getHashes() const { return hashes; }
  unsigned int getMatchCount() const { return suspicious_matches.size(); }
  float getPercentage() const;

  // MODIFIERS
  void addHash(const hash &h, location_in_submission l) { hashes.push_back(std::make_pair(h, l)); }
  void addSuspiciousMatch(location_in_submission location, const HashLocation &matching_location, const hash &matched_hash);
  void addCommonMatch(location_in_submission location);
  void addProvidedMatch(location_in_submission location);

private:
  user_id student_;
  version_number version_;
  LichenConfig config_;
  std::vector<std::pair<hash, location_in_submission> > hashes;
  std::map<location_in_submission, std::set<HashLocation> > suspicious_matches;
  std::set<location_in_submission> common_matches;
  std::set<location_in_submission> provided_matches;

  // a container to keep track of all the students this submission
  // matched and the number of matching hashes per submission
  // <source_gradeable, <username, <version, <hashes>> > >
  std::unordered_map<std::string, std::unordered_map<user_id, std::unordered_map<version_number, std::unordered_set<hash>>>> students_matched;
};

#endif
