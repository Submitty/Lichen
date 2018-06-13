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
// helper classes


// A submission is the concatenated files for one submission version
// for a user.
class Submission {
public:
  Submission(std::string u, std::string v) : username(u),version(v) {}
  std::string username;
  std::string version;
};

// to allow sorting
bool operator<(const Submission &a, const Submission &b) {
  return a.username < b.username ||
                      (a.username == b.username && a.version < b.version);
}


// A sequence is represented by the start location (integer index of
// the token) within in a specific concatenated file (the Submission).
class Sequence {
public:
  Sequence(std::string u, std::string v, int p) : submission(u,v),position(p) {}
  Submission submission;
  int position;
};


// ===================================================================================
// helper typedefs


// common sequence hash -> ( each user -> all match locations by that user across all versions )
typedef std::map<std::string,std::map<std::string,std::vector<Sequence> > > hashed_sequences;



// ===================================================================================
// helper functions


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
int main(int argc, char* argv[]) {

  std::cout << "COMPARE HASHES...";
  fflush(stdout);


  // ---------------------------------------------------------------------------
  // deal with command line arguments
  assert (argc == 4);
  std::string semester = argv[1];
  std::string course = argv[2];
  std::string gradeable = argv[3];


  // error checking, confirm there are hashes to work with
  std::string tmp = "/var/local/submitty/courses/"+semester+"/"+course+"/lichen/hashes/"+gradeable;
  boost::filesystem::path hashes_root_directory = boost::filesystem::system_complete(tmp);
  if (!boost::filesystem::exists(hashes_root_directory) ||
      !boost::filesystem::is_directory(hashes_root_directory)) {
    std::cerr << "ERROR with directory " << hashes_root_directory << std::endl;
    exit(0);
  }


  // store the total size (# of tokens) in each submission
  std::map<Submission,int> submission_length;


  // ---------------------------------------------------------------------------
  // loop over all submissions and populate the hash_counts structure

  // the main data structure that looks for matches between submissions
  hashed_sequences hash_counts;

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
      std::string version = username_itr->path().filename().string();
      // load the hashes sequences from this submission
      boost::filesystem::path hash_file = version_path;
      hash_file /= "hashes.txt";
      std::ifstream istr(hash_file.string());
      std::string tmp;
      int count = 0;
      while (istr >> tmp) {
        count++;
        hash_counts[tmp][username].push_back(Sequence(username,version,count));
      }
      submission_length[Submission(username,version)]=count;
    }    
  }

  // ---------------------------------------------------------------------------

  // label the parts of the file that are common to many
  // user,version -> vector<position>
  std::map<Submission,std::vector<int> > common;

  // label the parts of the file that match the provided code
  // user,version -> vector<position>
  std::map<Submission,std::vector<int> > provided;
  
  // document the suspicious parts of this file,
  // user,version -> ( position -> ( other user,version -> std::vector<Sequence> ) )
  std::map<Submission,std::map<int,std::map<Submission, std::vector<Sequence> > > > suspicious;


  // ---------------------------------------------------------------------------
  // walk over the structure containing all of the hashes identifying
  // common to many/all, provided code, suspicious matches, and unique code
  for (hashed_sequences::iterator itr = hash_counts.begin(); itr != hash_counts.end(); itr++) {
    int count = itr->second.size();

    if (count >= 20) {
      // common to many/all
      for (std::map<std::string,std::vector<Sequence> >::iterator itr2 = itr->second.begin(); itr2 != itr->second.end(); itr2++) {
        for (int i = 0; i < itr2->second.size(); i++) {
          common[itr2->second[i].submission].push_back(itr2->second[i].position);
        }
      }
    } else if (count > 1 && count < 20) {
      // suspicious matches
      for (std::map<std::string,std::vector<Sequence> >::iterator itr2 = itr->second.begin(); itr2 != itr->second.end(); itr2++) {
        std::string username = itr2->first;
        for (int i = 0; i < itr2->second.size(); i++) {
          assert (itr2->second[i].submission.username == username);
          std::string version = itr2->second[i].submission.version;
          int position = itr2->second[i].position;

          std::map<Submission, std::vector<Sequence> > matches;
          
          for (std::map<std::string,std::vector<Sequence> >::iterator itr3 = itr->second.begin(); itr3 != itr->second.end(); itr3++) {
            std::string match_username = itr3->first;
            for (int j = 0; j < itr3->second.size(); j++) {
              std::string match_version = itr3->second[j].submission.version;
              Submission ms(match_username,match_version);
              matches[ms].push_back(itr3->second[j]);
            }
          }
          Submission s(username,version);
          suspicious[s][position]=matches;
        }
      }
    }
  }


  // ---------------------------------------------------------------------------
  // prepare a sorted list of all users sorted by match percent
  std::vector<std::pair<Submission,float> > ranking;
  for (std::map<Submission,std::map<int,std::map<Submission,std::vector<Sequence> > > >::iterator itr = suspicious.begin();
       itr != suspicious.end(); itr++) {
    int total = submission_length[itr->first];
    int overlap = itr->second.size();
    float percent = float(overlap)/float(total);

    std::vector<nlohmann::json> info;

    std::string username = itr->first.username;
    std::string version = itr->first.version;

    ranking.push_back(std::make_pair(itr->first,percent));

    // prepare the ranges of suspicious matching tokens
    int range_start=-1;
    int range_end=-1;
    for (std::map<int,std::map<Submission,std::vector<Sequence> > >::iterator itr2 = itr->second.begin(); itr2 != itr->second.end(); itr2++) {
      int pos = itr2->first;
      if (range_start==-1) {
        range_start = range_end = pos;
      } else if (range_end+1 == pos) {
        range_end = pos;
      } else {
        std::map<std::string,std::string> info_data;
        info_data["start"]=std::to_string(range_start);
        info_data["end"]=std::to_string(range_end);
        info_data["type"]=std::string("match");
        info.push_back(info_data);
        range_start=range_end=-1;
      }
    }
    if (range_start != -1) {
      std::map<std::string,std::string> info_data;
      info_data["start"]=std::to_string(range_start);
      info_data["end"]=std::to_string(range_end);
      info_data["type"]=std::string("match");
      info.push_back(info_data);
      range_start=range_end=-1;
    }

    // save the file with matches per user
    nlohmann::json match_data = info;
    std::string matches_dir = "/var/local/submitty/courses/"+semester+"/"+course+"/lichen/matches/"+gradeable+"/"+username+"/"+version;
    boost::filesystem::create_directories(matches_dir);
    std::string matches_file = matches_dir+"/matches.json";
    std::ofstream ostr(matches_file);
    assert (ostr.good());
    ostr << match_data.dump(4) << std::endl;
  }

  // save the rankings to a file
  std::string ranking_dir = "/var/local/submitty/courses/"+semester+"/"+course+"/lichen/ranking/";
  std::string ranking_file = ranking_dir+gradeable+".txt";
  boost::filesystem::create_directories(ranking_dir);
  std::ofstream ranking_ostr(ranking_file);
  std::sort(ranking.begin(),ranking.end(),ranking_sorter);
  for (int i = 0; i < ranking.size(); i++) {
    ranking_ostr
      << std::setw(6) << std::setprecision(2) << std::fixed << 100.0*ranking[i].second << "%   "
      << std::setw(15) << std::left << ranking[i].first.username << " "
      << std::setw(3) << std::right << ranking[i].first.version << std::endl;
  }

  
  // ---------------------------------------------------------------------------
  std::cout << "done" << std::endl;
}
