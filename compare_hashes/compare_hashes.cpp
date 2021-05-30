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

using namespace std;

// ===================================================================================
// helper classes

// represents the location of a hash within 
// a unique student and version pair
struct HashLocation {
  HashLocation(const string &s, int v, location_in_submission l) : student(s), version(v), location(l) {}
  string student;
  int version;
  location_in_submission location;
};

// represents a unique student-version pair, all its 
// hashes, and other submissions with those hashes
class Submission {
public:
  Submission(const string &s, int v) : student_(s), version_(v) {}
  const string & student() const { return student_; }
  int version() const { return version_; }
  void addHash(const hash &h, location_in_submission l) { hashed.push_back(make_pair(h, l)); }
  const vector<pair<hash, location_in_submission>> & getHashes() const { return hashes; }
  void addSuspiciousMatch(location_in_submission location, const HashLocation &matching_location) {
    map<location_in_submission, vector<HashLocation>>::iterator itr =  suspicious_matches.find(location);
    if (itr != suspicious_matches.end()) {
      // location already exists in the map, so we just append the location to the vector
      suspicious_matches[location].push_back(matching_location);
    } else {
      // intialize the vector and add the location
      vector<HashLocation> v();
      v.push_back(matching_location);
      suspicious_matches[location] = v;
    }
  }

private:
  string student_;
  int version_;
  vector<pair<hash, location_in_submission>> hashes;
  map<location_in_submission, vector<HashLocation>> suspicious_matches;
};


// ===================================================================================
// helper typedefs

typedef int location_in_submission;
typedef string hash;


// ===================================================================================
// helper functions


// TODO: remake functions
/*
// Orders all Submissions by percentage of tokens in that match tokens
// in a small number of other files (but not most or all).
bool ranking_sorter(const std::pair<Submission,float> &a, const std::pair<Submission,float> &b) {
  return
    a.second > b.second ||
    (a.second == b.second && a.first.username < b.first.username) ||
    (a.second == b.second && a.first.username == b.first.username && a.first.version < b.first.version);
}


// ===================================================================================
// ===================================================================================
void insert_others(const std::string &this_username,
                   std::map<Submission,std::set<int> > &others,
                   const std::map<Submission,std::vector<Sequence> > &matches) {
  for (std::map<Submission,std::vector<Sequence> >::const_iterator itr = matches.begin(); itr!=matches.end();itr++) {
    for (unsigned int i = 0; i < itr->second.size(); i++) {
      // don't include matches to this username
      if (this_username == itr->first.username)
        continue;
      others[itr->first].insert(itr->second[i].position);
    }
  }
}

void convert(std::map<Submission,std::set<int> > &myset, nlohmann::json &obj, int sequence_length) {
  for (std::map<Submission,std::set<int> >::iterator itr = myset.begin(); itr != myset.end(); itr++) {
    nlohmann::json me;
    me["username"] = itr->first.username;
    me["version"] = itr->first.version;

    std::vector<nlohmann::json> foo;
    int start = -1;
    int end = -1;
    std::set<int>::iterator itr2 = itr->second.begin();
    for (; itr2 != itr->second.end(); itr2++) {
  		start = *itr2;
  		end = start + sequence_length;
  		nlohmann::json range;
  		range["start"] = start;
  		range["end"] = end;
  		foo.push_back(range);
    }
    me["matchingpositions"] = foo;
    obj.push_back(me);
  }
}


// ensures that all of the regions in the two parameters are adjacent
bool matchingPositionsAreAdjacent(const nlohmann::json &first, const nlohmann::json &second) {
  // they can't all be adjacent if there are an unequal number between the two lists
  if (first.size() != second.size()) {
    return false;
  }

  nlohmann::json::const_iterator itr1 = first.begin();
  nlohmann::json::const_iterator itr2 = second.begin();
  // iterate over each matching submission
  for (; itr1 != first.end() && itr2 != second.end(); itr1++, itr2++) {
    // the number of matches must be the same
    if ((*itr1)["matchingpositions"].size() != (*itr2)["matchingpositions"].size()) {
      return false;
    }

    nlohmann::json::const_iterator itr3 = (*itr1)["matchingpositions"].begin();
    nlohmann::json::const_iterator itr4 = (*itr2)["matchingpositions"].begin();
    // iterate over each matching position in the submission
    for (; itr3 != (*itr1)["matchingpositions"].end() && itr4 != (*itr2)["matchingpositions"].end(); itr3++, itr4++) {
      if ((*itr3)["end"].get<int>() + 1 != (*itr4)["end"].get<int>()) {
        return false;
      }
    }
  }
  return true;
}

// increments the end position for each of the matches in the json provided
void incrementEndPositionsForMatches(nlohmann::json &matches) {
  nlohmann::json::iterator itr = matches.begin();
  for (; itr != matches.end(); itr++) {
    nlohmann::json::iterator itr2 = (*itr)["matchingpositions"].begin();
    for (; itr2 != (*itr)["matchingpositions"].end(); itr2++) {
      (*itr2)["end"] = (*itr2)["end"].get<int>() + 1;
    }
  }
}
*/

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

  // Stores all the hashes and their locations across all submissions
  unordered_map<hash, vector<HashLocation>> all_hashes;
  // Stores all submissions
  vector<Submission> all_submissions;

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

      // create a submission object and load to the main submission structure
      Submission submission(username, version);
      all_submissions.push_back(submission);

      // load the hashes sequences from this submission
      boost::filesystem::path hash_file = version_path;
      hash_file /= "hashes.txt";
      std::ifstream istr(hash_file.string());
      hash input_hash;
      int location = 0;
      while (istr >> input_hash) {
        location++;
        all_hashes[input_hash].push_back(HashLocation(username, version, location));
        submission.addHash(input_hash, location);
      }
    }
  }

  std::cout << "finished loading" << std::endl;

  // ---------------------------------------------------------------------------
  // THIS IS THE MAIN PLAGIARISM DETECTION ALGORITHM

  // Used to calculate current progress (printed to the log)
  int my_counter = 0;
  int my_percent = 0;

  // ---------------------------------------------------------------------------
  
  //unordered_map<hash, vector<HashLocation>> all_hashes;
  //vector<Submission> all_submissions;

  // walk over every Submission 
  for (vector<Submission>::iterator submission_itr = all_submissions.begin(); 
       submission_itr != all_submissions.end(); ++submission_itr) {
    
    // walk over every hash in that submission
    vector<pair<hash, location_in_submission>>::const_iterator hash_itr = submission_itr->getHashes().begin();
    for (; hash_itr != submission_itr->getHashes().end(); ++hash_itr) {
      
      // look up that hash in the all_hashes table, and see which other occurences of that hash in other submisions
      vector<HashLocation> occurences = all_hashes[hash_itr->first]->second; // TODO: Optimize?
      vector<HashLocation>::iterator occurences_itr = occurences.begin();
      for (; occurences_itr != occurences.end(); ++occurences_itr) {
        if (occurences_itr->name != submission_itr->student()) {
          // SUS MATCH. 
          submission_itr->addSuspiciousMatch(hash_itr->second, *occurences_itr);
        }
      }
    }
  }

  std::cout << "finished walking" << std::endl;

  // ---------------------------------------------------------------------------
  // prepare a sorted list of all users sorted by match percent
  std::vector<std::pair<Submission,float> > ranking;

  my_counter = 0;
  my_percent = 0;
  std::cout << "merging regions and writing matches files..." << std::endl;
  for (std::map<Submission,std::map<int,std::map<Submission,std::vector<Sequence> > > >::iterator itr = suspicious.begin();
       itr != suspicious.end(); itr++) {
    int total = submission_length[itr->first];
    int overlap = itr->second.size();
    float percent = float(overlap)/float(total);

    std::vector<nlohmann::json> info;

    std::string username = itr->first.username;
    int version = itr->first.version;

    ranking.push_back(std::make_pair(itr->first,percent));

    // prepare the ranges of suspicious matching tokens
    int range_start = -1;
    int range_end = -1;
    std::map<Submission, std::set<int> > others;

    for (std::map<int, std::map<Submission, std::vector<Sequence> > >::iterator itr2 = itr->second.begin();
         itr2 != itr->second.end(); itr2++) {
    	range_start = itr2->first;
    	range_end = range_start + sequence_length;
    	insert_others(username, others, itr2->second);
    	std::map<std::string, nlohmann::json> info_data;
    	info_data["start"] = nlohmann::json(range_start);
    	info_data["end"] = nlohmann::json(range_end);
    	info_data["type"] = nlohmann::json(std::string("match"));
    	nlohmann::json obj;
    	convert(others, obj, sequence_length);
    	info_data["others"] = obj;
    	info.push_back(info_data);
    	others.clear();
    }

    // Merge matching regions:
    if (info.size() > 0) { // check to make sure that there are more than 1 positions (if it's 1, we can't merge anyway)
      // loop through all positions
      for (unsigned int position = 1; position < info.size(); position++) {
        nlohmann::json* prevPosition = &info[position - 1];
        nlohmann::json* currPosition = &info[position];
        if ((*currPosition)["end"].get<int>() == (*prevPosition)["end"].get<int>() + 1) { // check whether they are next to each other
          bool canBeMerged = true;
          nlohmann::json::iterator prevPosItr = (*prevPosition)["others"].begin();
          nlohmann::json::iterator currPosItr = (*currPosition)["others"].begin();
          if ((*prevPosition)["others"].size() != (*currPosition)["others"].size()) {
            canBeMerged = false;
          }
          else {
            for (; prevPosItr != (*prevPosition)["others"].end() && currPosItr != (*currPosition)["others"].end(); prevPosItr++, currPosItr++) {
              // we can't merge the two positions if they are different in any way, except for the ending positions
              if ((*prevPosItr)["username"] != (*currPosItr)["username"] ||
                  (*prevPosItr)["version"] != (*currPosItr)["version"] ||
                  !matchingPositionsAreAdjacent((*prevPosItr)["others"], (*currPosItr)["others"])) {
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

            info.erase(info.begin() + position);
            position--;
          }
        }
      }
    }

    // save the file with matches per user
    nlohmann::json match_data = info;
    std::string matches_dir = "/var/local/submitty/courses/"+semester+"/"+course+"/lichen/matches/"+gradeable+"/"+username+"/"+std::to_string(version);
    boost::filesystem::create_directories(matches_dir);
    std::string matches_file = matches_dir+"/matches.json";
    std::ofstream ostr(matches_file);
    assert(ostr.good());
    ostr << match_data.dump(4) << std::endl;

    my_counter++;
    if (int((my_counter / float(suspicious.size())) * 100) > my_percent) {
      my_percent = int((my_counter / float(suspicious.size())) * 100);
      std::cout << "merging: " << my_percent << "% complete" << std::endl;
    }
  }
  std::cout << "done merging and writing matches files" << std::endl;

  std::set<std::string> users_already_ranked;

  // save the rankings to a file
  std::string ranking_dir = "/var/local/submitty/courses/"+semester+"/"+course+"/lichen/ranking/";
  std::string ranking_file = ranking_dir+gradeable+".txt";
  boost::filesystem::create_directories(ranking_dir);
  std::ofstream ranking_ostr(ranking_file);
  std::sort(ranking.begin(),ranking.end(),ranking_sorter);
  for (unsigned int i = 0; i < ranking.size(); i++) {
    std::string username = ranking[i].first.username;
    if (users_already_ranked.insert(username).second != false) {
      // print each username at most once, only if insert was
      // successful (not already in the set)
      ranking_ostr
        << std::setw(6) << std::setprecision(2) << std::fixed << 100.0*ranking[i].second << "%   "
        << std::setw(15) << std::left << ranking[i].first.username << " "
        << std::setw(3) << std::right << ranking[i].first.version << std::endl;
    }
  }


  // ---------------------------------------------------------------------------
  std::cout << "done" << std::endl;
}
