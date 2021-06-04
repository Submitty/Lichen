#include <iostream>
#include <map>
#include <unordered_map>
#include <cassert>
#include <string>
#include <cstdlib>
#include <fstream>
#include <set>
#include <iomanip>

#include "boost/filesystem/operations.hpp"
#include "boost/filesystem/path.hpp"

#include "nlohmann/json.hpp"


// ===================================================================================
// helper typedefs

typedef int location_in_submission;
typedef std::string hash;


// ===================================================================================
// helper classes

// represents the location of a hash within
// a unique student and version pair
struct HashLocation {
  HashLocation(const std::string &s, int v, location_in_submission l) : student(s), version(v), location(l) {}
  std::string student;
  int version;
  location_in_submission location;
};


// represents an element in a ranking of students by percent match
struct StudentRanking {
  StudentRanking(const std::string &s, int v, float p) : student(s), version(v), percent(p) {}
  std::string student;
  int version;
  float percent;
};


// represents a unique student-version pair, all its
// hashes, and other submissions with those hashes
class Submission {
public:
  Submission(const std::string &s, int v) : student_(s), version_(v) {}
  const std::string & student() const { return student_; }
  int version() const { return version_; }
  void addHash(const hash &h, location_in_submission l) { hashes.push_back(make_pair(h, l)); }
  const std::vector<std::pair<hash, location_in_submission>> & getHashes() const { return hashes; }
  void addSuspiciousMatch(location_in_submission location, const HashLocation &matching_location) {
    std::map<location_in_submission, std::set<HashLocation>>::iterator itr = suspicious_matches.find(location);
    // TODO: is this if-else necessary? would this not work if we just did?: suspicious_matches[location].insert(matching_location);
    if (itr != suspicious_matches.end()) {
      // location already exists in the map, so we just append the location to the set
      suspicious_matches[location].insert(matching_location);
    } else {
      // intialize the set and add the location
      std::set<HashLocation> s;
      s.insert(matching_location);
      suspicious_matches[location] = s;
    }
    // update the students_matched container
    students_matched[matching_location.student][matching_location.version]++;
  }
  void addCommonMatch(location_in_submission location, const HashLocation &matching_location) {
    std::map<location_in_submission, std::set<HashLocation>>::iterator itr = common_matches.find(location);

    if (itr != common_matches.end()) {
      // location already exists in the map, so we just append the location to the set
      common_matches[location].insert(matching_location);
    } else {
      // intialize the set and add the location
      std::set<HashLocation> s;
      s.insert(matching_location);
      common_matches[location] = s;
    }
  }
  const std::map<location_in_submission, std::set<HashLocation> >& getSuspiciousMatches() const {
    return suspicious_matches;
  }
  const std::map<location_in_submission, std::set<HashLocation> >& getCommonMatches() const {
    return common_matches;
  }
  const std::unordered_map<std::string, std::unordered_map<int, int> >& getStudentsMatched() const {
    return students_matched;
  }
  unsigned int getNumHashes() const { return hashes.size(); }
  float getPercentage() const {
    return (100.0 * (suspicious_matches.size() + common_matches.size())) / hashes.size();
  }

private:
  std::string student_;
  int version_;
  std::vector<std::pair<hash, location_in_submission> > hashes;
  std::map<location_in_submission, std::set<HashLocation> > suspicious_matches;
  std::map<location_in_submission, std::set<HashLocation> > common_matches;

  // a container to keep track of all the students this submission
  // matched and the number of matching hashes per submission
  std::unordered_map<std::string, std::unordered_map<int, int> > students_matched;
};


// ===================================================================================
// helper functions

bool operator < (const HashLocation &hl1, const HashLocation &hl2) {
  return hl1.student > hl2.student ||
         (hl1.student == hl2.student && hl1.version < hl2.version) ||
         (hl1.student == hl2.student && hl1.version == hl2.version && hl1.location < hl2.location);
}


// ensures that all of the regions in the two parameters are adjacent
bool matchingPositionsAreAdjacent(const nlohmann::json &first, const nlohmann::json &second) {
  // they can't all be adjacent if there are an unequal number between the two lists
  if (first["matchingpositions"].size() != second["matchingpositions"].size()) {
    return false;
  }

  nlohmann::json::const_iterator itr1 = first["matchingpositions"].begin();
  nlohmann::json::const_iterator itr2 = second["matchingpositions"].begin();
  // iterate over each matching submission (first and second are the same length so we don't have to check for the end of second)
  for (; itr1 != first["matchingpositions"].end(); itr1++, itr2++) {
    if ((*itr1)["end"].get<int>() + 1 != (*itr2)["end"].get<int>()) {
      return false;
    }
  }
  return true;
}


// increments the end position for each of the matches in the json provided,
// merging overlapping regions where necessary
void incrementEndPositionsForMatches(nlohmann::json &others) {
  nlohmann::json::iterator itr = others.begin();
  for (; itr != others.end(); itr++) {
    nlohmann::json::iterator itr2 = (*itr)["matchingpositions"].begin();
    nlohmann::json::iterator itr3 = ++((*itr)["matchingpositions"].begin());
    for (; itr3 != (*itr)["matchingpositions"].end();) {
      if ((*itr2)["end"].get<int>() >= (*itr3)["start"]) {
        (*itr2)["end"] = (*itr3)["end"].get<int>();
        itr3 = (*itr)["matchingpositions"].erase(itr3);
      }
      else {
        (*itr2)["end"] = (*itr2)["end"].get<int>() + 1;
        itr2++;
        itr3++;
      }
    }
    (*itr2)["end"] = (*itr2)["end"].get<int>() + 1;
  }
}


bool ranking_sorter(const StudentRanking &a, const StudentRanking &b) {
  return a.percent > b.percent ||
        (a.percent == b.percent && a.student < b.student);
}


// ===================================================================================
// ===================================================================================
int main(int argc, char* argv[]) {

  std::cout << "COMPARE HASHES...";
  fflush(stdout);

  // ---------------------------------------------------------------------------
  // deal with command line arguments

  assert (argc == 2);
  std::string config_file = argv[1];

  std::ifstream istr(config_file.c_str());
  assert (istr.good());
  nlohmann::json config_file_json = nlohmann::json::parse(istr);

  std::string semester = config_file_json.value("semester","ERROR");
  std::string course = config_file_json.value("course","ERROR");
  std::string gradeable = config_file_json.value("gradeable","ERROR");
  std::string sequence_length_str = config_file_json.value("sequence_length","1");
  int sequence_length = std::stoi(sequence_length_str);
  std::string threshold_str = config_file_json.value("threshold","5");
  int threshold = std::stoi(threshold_str);

  assert (sequence_length >= 1);
  assert (threshold >= 2);

  // error checking, confirm there are hashes to work with
  std::string tmp = "/var/local/submitty/courses/"+semester+"/"+course+"/lichen/hashes/"+gradeable;
  boost::filesystem::path hashes_root_directory = boost::filesystem::system_complete(tmp);
  if (!boost::filesystem::exists(hashes_root_directory) ||
      !boost::filesystem::is_directory(hashes_root_directory)) {
    std::cerr << "ERROR with directory " << hashes_root_directory << std::endl;
    exit(0);
  }

  // ---------------------------------------------------------------------------
  // loop over all submissions and populate the all_hashes and all_submissions structures

  // Stores all the hashes and their locations across all submissions (sorted in "bins" of student names)
  std::unordered_map<hash, std::unordered_map<std::string, std::vector<HashLocation>>> all_hashes;
  // Stores all submissions
  std::vector<Submission> all_submissions;

  // loop over all users
  boost::filesystem::directory_iterator end_iter;
  for (boost::filesystem::directory_iterator dir_itr( hashes_root_directory ); dir_itr != end_iter; ++dir_itr) {
    boost::filesystem::path username_path = dir_itr->path();
    assert (is_directory(username_path));
    std::string username = dir_itr->path().filename().string();

    // loop over all versions
    for (boost::filesystem::directory_iterator username_itr( username_path ); username_itr != end_iter; ++username_itr) {
      boost::filesystem::path version_path = username_itr->path();
      assert (is_directory(version_path));
      std::string str_version = username_itr->path().filename().string();
      int version = std::stoi(str_version);
      assert (version > 0);

      // create a submission object and load to the main submissions structure
      Submission submission(username, version);

      // load the hashes from this submission
      boost::filesystem::path hash_file = version_path;
      hash_file /= "hashes.txt";
      std::ifstream istr(hash_file.string());
      hash input_hash;
      int location = 0;
      while (istr >> input_hash) {
        location++;
        all_hashes[input_hash][username].push_back(HashLocation(username, version, location));
        submission.addHash(input_hash, location);
      }

      all_submissions.push_back(submission);
    }
  }

  std::cout << "finished loading" << std::endl;

  // ---------------------------------------------------------------------------
  // THIS IS THE MAIN PLAGIARISM DETECTION ALGORITHM

  // Used to calculate current progress (printed to the log)
  int my_counter = 0;
  int my_percent = 0;

  // walk over every Submission
  for (std::vector<Submission>::iterator submission_itr = all_submissions.begin();
       submission_itr != all_submissions.end(); ++submission_itr) {

    // walk over every hash in that submission
    std::vector<std::pair<hash, location_in_submission>>::const_iterator hash_itr = submission_itr->getHashes().begin();
    for (; hash_itr != submission_itr->getHashes().end(); ++hash_itr) {

      // look up that hash in the all_hashes table, loop over all other students that have the same hash
      std::unordered_map<std::string, std::vector<HashLocation>> occurences = all_hashes[hash_itr->first];
      std::unordered_map<std::string, std::vector<HashLocation>>::iterator occurences_itr = occurences.begin();
      for (; occurences_itr != occurences.end(); ++occurences_itr) {

        // don't look for matches across submissions of the same student
        if (occurences_itr->first == submission_itr->student()) {
          continue;
        }

        // save the locations of all other occurences of the matching hash in other students' submissions
        std::vector<HashLocation>::iterator itr = occurences_itr->second.begin();
        for (; itr != occurences_itr->second.end(); ++itr) {

          if (occurences.size() > (unsigned int)threshold) {
            // if the number of students with matching code is more
            // than the threshold, it is considered common code
            submission_itr->addCommonMatch(hash_itr->second, *itr);
          } else {
            // save the match as a suspicous match
            submission_itr->addSuspiciousMatch(hash_itr->second, *itr);
          }
          // TODO: insert provided match here
        }
      }
    }

    // print current progress
    my_counter++;
    if (int((my_counter / float(all_submissions.size())) * 100) > my_percent) {
      my_percent = int((my_counter / float(all_submissions.size())) * 100);
      std::cout << "hash walk: " << my_percent << "% complete" << std::endl;
    }
  }

  std::cout << "finished walking" << std::endl;

  // ---------------------------------------------------------------------------
  // Writing the output files and merging the results

  my_counter = 0;
  my_percent = 0;
  std::cout << "writing matches files and merging regions..." << std::endl;

  // Loop over all of the submissions, writing a JSON file for each one if it has suspicious matches
  for (std::vector<Submission>::iterator submission_itr = all_submissions.begin();
       submission_itr != all_submissions.end(); ++submission_itr) {
    // If there are no suspicious matches, don't create a JSON file
    if (submission_itr->getSuspiciousMatches().size() == 0) {
      continue;
    }
    // holds the JSON file to be written
    std::vector<nlohmann::json> result;


    // ********  WRITE THE SUSPICIOUS MATCHES  ********
    // all of the suspicious matches for this submission
    std::map<location_in_submission, std::set<HashLocation> > suspicious_matches = submission_itr->getSuspiciousMatches();

    // loop over each of the suspicious locations in the current submission
    for (std::map<location_in_submission, std::set<HashLocation> >::const_iterator location_itr
         =suspicious_matches.begin(); location_itr != suspicious_matches.end(); ++location_itr) {

      // stores matches of hash locations across other submssions in the class
      std::vector<nlohmann::json> others;

      {
        // generate a specific element of the "others" vector
        // set the variables to their initial values
        std::set<HashLocation>::const_iterator matching_positions_itr = location_itr->second.begin();
        nlohmann::json other;
        other["username"] = matching_positions_itr->student;
        other["version"] = matching_positions_itr->version;
        std::vector<nlohmann::json> matchingpositions;
        nlohmann::json position;
        position["start"] = matching_positions_itr->location;
        position["end"] = matching_positions_itr->location + sequence_length - 1;
        matchingpositions.push_back(position);

        // search for all matching positions of the suspicious match in other submissions
        if (location_itr->second.size() > 1) {
          ++matching_positions_itr;

          // loop over all of the other matching positions
          for (; matching_positions_itr != location_itr->second.end(); ++matching_positions_itr) {

            // keep iterating and editing the same object until a we get to a different submission
            if (matching_positions_itr->student != other["username"] || matching_positions_itr->version != other["version"]) {
              // found a different one, we push the old one and start over
              other["matchingpositions"] = matchingpositions;
              others.push_back(other);

              matchingpositions.clear();
              other["username"] = matching_positions_itr->student;
              other["version"] = matching_positions_itr->version;
            }
            position["start"] = matching_positions_itr->location;
            position["end"] = matching_positions_itr->location + sequence_length - 1;
            matchingpositions.push_back(position);
          }
        }

        other["matchingpositions"] = matchingpositions;
        others.push_back(other);
      }

      nlohmann::json info;
      info["start"] = location_itr->first;
      info["end"] = location_itr->first + sequence_length - 1;
      info["type"] = "match";
      info["others"] = others;

      result.push_back(info);
    }
    // ********************************************

    // ********  WRITE THE COMMON MATCHES  ********
    // all of the common matches for this submission
    std::map<location_in_submission, std::set<HashLocation> > common_matches = submission_itr->getCommonMatches();

    // loop over each of the common locations in the current submission
    for (std::map<location_in_submission, std::set<HashLocation> >::const_iterator location_itr
         =common_matches.begin(); location_itr != common_matches.end(); ++location_itr) {

      // stores matches of hash locations across other submssions in the class
      std::vector<nlohmann::json> others;

      {
        // generate a specific element of the "others" vector
        // set the variables to their initial values
        std::set<HashLocation>::const_iterator matching_positions_itr = location_itr->second.begin();
        nlohmann::json other;
        other["username"] = matching_positions_itr->student;
        other["version"] = matching_positions_itr->version;
        std::vector<nlohmann::json> matchingpositions;
        nlohmann::json position;
        position["start"] = matching_positions_itr->location;
        position["end"] = matching_positions_itr->location + sequence_length - 1;
        matchingpositions.push_back(position);

        // search for all matching positions of the suspicious match in other submissions
        if (location_itr->second.size() > 1) {
          ++matching_positions_itr;

          // loop over all of the other matching positions
          for (; matching_positions_itr != location_itr->second.end(); ++matching_positions_itr) {

            // keep iterating and editing the same object until a we get to a different submission
            if (matching_positions_itr->student != other["username"] || matching_positions_itr->version != other["version"]) {
              // found a different one, we push the old one and start over
              other["matchingpositions"] = matchingpositions;
              others.push_back(other);

              matchingpositions.clear();
              other["username"] = matching_positions_itr->student;
              other["version"] = matching_positions_itr->version;
            }
            position["start"] = matching_positions_itr->location;
            position["end"] = matching_positions_itr->location + sequence_length - 1;
            matchingpositions.push_back(position);
          }
        }

        other["matchingpositions"] = matchingpositions;
        others.push_back(other);
      }

      nlohmann::json info;
      info["start"] = location_itr->first;
      info["end"] = location_itr->first + sequence_length - 1;
      info["type"] = "common";
      info["others"] = others;

      result.push_back(info);
    }
    // ********************************************


    // ---------------------------------------------------------------------------
    // Done creating the JSON file/objects, now we merge them to shrink them in size

    // Merge matching regions:
    if (result.size() > 0) { // check to make sure that there are more than 1 positions (if it's 1, we can't merge anyway)
      // loop through all positions
      for (unsigned int position = 1; position < result.size(); position++) {
        nlohmann::json* prevPosition = &result[position - 1];
        nlohmann::json* currPosition = &result[position];
        // check whether they are next to each other and have the same type
        if ((*currPosition)["end"].get<int>() == (*prevPosition)["end"].get<int>() + 1 && (*currPosition)["type"] == (*prevPosition)["type"]) {
          bool canBeMerged = true;
          // easy check to see if they can't be merged for certain
          if ((*prevPosition)["others"].size() != (*currPosition)["others"].size()) {
            canBeMerged = false;
          }
          else {
            nlohmann::json::iterator prevPosItr = (*prevPosition)["others"].begin();
            nlohmann::json::iterator currPosItr = (*currPosition)["others"].begin();
            for (; prevPosItr != (*prevPosition)["others"].end() && currPosItr != (*currPosition)["others"].end(); prevPosItr++, currPosItr++) {
              // we can't merge the two positions if they are different in any way, except for the ending positions
              if ((*prevPosItr)["username"] != (*currPosItr)["username"] ||
                  (*prevPosItr)["version"] != (*currPosItr)["version"] ||
                  !matchingPositionsAreAdjacent((*prevPosItr), (*currPosItr))) {
                canBeMerged = false;
                break;
              }
            }
          }

          //if it's possible to do the merging, do it here by adjusting the end of the previous position and erasing the current position
          if (canBeMerged) {
            (*prevPosition)["end"] = (*currPosition)["end"].get<int>(); // (should be the equivalent of prevPosition["end"]++)

            // increment end positions for each element
            incrementEndPositionsForMatches((*prevPosition)["others"]);

            result.erase(result.begin() + position);
            position--;
          }
        }
      }
    }

    // save the file with matches per user
    nlohmann::json match_data = result;
    std::string matches_dir = "/var/local/submitty/courses/"+semester+"/"+course
        +"/lichen/matches/"+gradeable+"/"+submission_itr->student()+"/"+std::to_string(submission_itr->version());
    boost::filesystem::create_directories(matches_dir);
    std::string matches_file = matches_dir+"/matches.json";
    std::ofstream ostr(matches_file);
    assert(ostr.good());
    ostr << match_data.dump(4) << std::endl;

    // printing out the progress
    my_counter++;
    if (int((my_counter / float(all_submissions.size())) * 100) > my_percent) {
      my_percent = int((my_counter / float(all_submissions.size())) * 100);
      std::cout << "merging: " << my_percent << "% complete" << std::endl;
    }

  }
  std::cout << "done merging and writing matches files" << std::endl;

  // ---------------------------------------------------------------------------
  // Create a general summary of rankings of users by percentage match

  // create a single file of students ranked by highest percentage of code plagiarised
  std::string ranking_dir = "/var/local/submitty/courses/"+semester+"/"+course+"/lichen/ranking/"+gradeable+"/";
  std::string ranking_file = ranking_dir+"overall_ranking.txt";
  boost::filesystem::create_directories(ranking_dir);
  std::ofstream ranking_ostr(ranking_file);

  // a map of students to a pair of the version and highest percent match for each student
  std::unordered_map<std::string, std::pair<int, float> > highest_matches;

  // loop over all the submissions, and find every student's version with the highest percentage
  for (std::vector<Submission>::iterator submission_itr = all_submissions.begin();
       submission_itr != all_submissions.end(); ++submission_itr) {

    float percentMatch = submission_itr->getPercentage();

    std::unordered_map<std::string, std::pair<int, float> >::iterator highest_matches_itr
        = highest_matches.find(submission_itr->student());
    if (highest_matches_itr == highest_matches.end()) {
      highest_matches[submission_itr->student()].first = submission_itr->version();
      highest_matches[submission_itr->student()].second = percentMatch;
    }
    else if (percentMatch > highest_matches_itr->second.second) {
      highest_matches_itr->second.first = submission_itr->version();
      highest_matches_itr->second.second = percentMatch;
    }
  }

  // take the map of highest matches and convert it to a vector so we can sort it
  // by percent match and then save it to a file
  std::vector<StudentRanking> ranking;
  for (std::unordered_map<std::string, std::pair<int, float> >::iterator itr
        = highest_matches.begin(); itr != highest_matches.end(); ++itr) {
    ranking.push_back(StudentRanking(itr->first, itr->second.first, itr->second.second));
  }

  std::sort(ranking.begin(), ranking.end(), ranking_sorter);

  for (unsigned int i = 0; i < ranking.size(); i++) {
    ranking_ostr
      << std::setw(6) << std::setprecision(2) << std::fixed << ranking[i].percent << "%   "
      << std::setw(15) << std::left << ranking[i].student << " "
      << std::setw(3) << std::right << ranking[i].version << std::endl;
  }


  // ---------------------------------------------------------------------------
  // create a rankings file for every submission. the file contains all the other
  // students share matches, sorted by decreasing order of the percent match

  for (std::vector<Submission>::iterator submission_itr = all_submissions.begin();
       submission_itr != all_submissions.end(); ++submission_itr) {

    // create the directory and a file to write into
    std::string ranking_student_dir = "/var/local/submitty/courses/"+semester+"/"+course+"/lichen/ranking/"
                                      +gradeable+"/"+submission_itr->student()+"/"+std::to_string(submission_itr->version())+"/";
    std::string ranking_student_file = ranking_student_dir+submission_itr->student()+"_"+std::to_string(submission_itr->version())+".txt";
    boost::filesystem::create_directories(ranking_student_dir);
    std::ofstream ranking_student_ostr(ranking_student_file);

    // find and sort the other submissions it matches with
    std::vector<StudentRanking> student_ranking;
    std::unordered_map<std::string, std::unordered_map<int, int> > matches = submission_itr->getStudentsMatched();
    for (std::unordered_map<std::string, std::unordered_map<int, int> >::const_iterator matches_itr = matches.begin();
         matches_itr != matches.end(); ++matches_itr) {

      for (std::unordered_map<int, int>::const_iterator version_itr = matches_itr->second.begin();
           version_itr != matches_itr->second.end(); ++version_itr) {

        // the percent match is currently calculated using the number of hashes that match between this
        // submission and the other submission, over the total number of hashes this submission has.
        // In other words, the percentage is how much of this submission's code was plgairised from the other.
        float percent = 100.0 * float(version_itr->second) / submission_itr->getNumHashes();
        student_ranking.push_back(StudentRanking(matches_itr->first, version_itr->first, percent));
      }
    }

    std::sort(student_ranking.begin(), student_ranking.end(), ranking_sorter);

    // finally, write the file of ranking for this submission
    for (unsigned int i = 0; i < student_ranking.size(); i++) {
      ranking_student_ostr
        << std::setw(6) << std::setprecision(2) << std::fixed << student_ranking[i].percent << "%   "
        << std::setw(15) << std::left << student_ranking[i].student << " "
        << std::setw(3) << std::right << student_ranking[i].version << std::endl;
    }
  }


  // ---------------------------------------------------------------------------
  std::cout << "done" << std::endl;

}
