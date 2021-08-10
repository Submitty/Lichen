#ifndef HASH_LOCATION_H
#define HASH_LOCATION_H

#include <string>
#include <unordered_map>

typedef int location_in_submission;
typedef unsigned int hash;
typedef std::string user_id;
typedef unsigned int version_number;

// represents the location of a hash within
// a unique student and version pair
struct HashLocation {
  HashLocation(const user_id &s, version_number v, location_in_submission l, const std::string &sg) : student(s), version(v), location(l), source_gradeable(sg) {}
  std::string student;
  version_number version;
  location_in_submission location;
  std::string source_gradeable;
};

bool operator < (const HashLocation &hl1, const HashLocation &hl2) {
  return hl1.student > hl2.student ||
         (hl1.student == hl2.student && hl1.version < hl2.version) ||
         (hl1.student == hl2.student && hl1.version == hl2.version && hl1.location < hl2.location);
}

#endif
