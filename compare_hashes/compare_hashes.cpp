#include <iostream>
#include <map>
#include <unordered_map>
#include <cassert>
#include <string>
#include <cstdlib>
#include <fstream>
#include <set>

#include "boost/filesystem/operations.hpp"
#include "boost/filesystem/path.hpp"


// -------------------------------------------------------
// helper class
class Specific {
public:
  Specific(std::string u, std::string v, int p) : username(u),version(v),position(p) {}
  std::string username;
  std::string version;
  int position;
};


typedef std::map<int,std::map<std::string,std::vector<Specific> > > specifics_map;


int main(int argc, char* argv[]) {

  std::cout << "COMPARE HASHES...";
  fflush(stdout);

  assert (argc == 4);
  
  std::string semester = argv[1];
  std::string course = argv[2];
  std::string gradeable = argv[3];

  std::string tmp = "/var/local/submitty/courses/"+semester+"/"+course+"/Lichen/hashes/"+gradeable;
  
  boost::filesystem::path hashes_root_directory = boost::filesystem::system_complete(tmp);
  if (!boost::filesystem::exists(hashes_root_directory) ||
      !boost::filesystem::is_directory(hashes_root_directory)) {
    std::cerr << "ERROR with directory " << hashes_root_directory << std::endl;
    exit(0);
  }


  specifics_map hash_counts;

  
  // LOOP OVER THE USERNAMES
  boost::filesystem::directory_iterator end_iter;
  for (boost::filesystem::directory_iterator dir_itr( hashes_root_directory ); dir_itr != end_iter; ++dir_itr) {
    boost::filesystem::path user_path = dir_itr->path();
    assert (is_directory(user_path));
    std::string username = dir_itr->path().filename().string();

    // LOOP OVER THE SUBMISSION VERSIONS
    for (boost::filesystem::directory_iterator user_itr( user_path ); user_itr != end_iter; ++user_itr) {
      boost::filesystem::path version_path = user_itr->path();
      assert (is_directory(version_path));
      std::string version = user_itr->path().filename().string();

      boost::filesystem::path hash_file = version_path;
      hash_file /= "hashes.txt";

      std::ifstream istr(hash_file.string());
      int tmp;
      int count = 0;
      while (istr >> tmp) {
        count++;
        hash_counts[tmp][username].push_back(Specific(username,version,count));
      }
    }    
  }


  std::map<std::string,std::set<int> > similarities;
  

  // WALK OVER THE MAP OF HASHES
  for (specifics_map::iterator itr = hash_counts.begin(); itr != hash_counts.end(); itr++) {
    int count = itr->second.size();


    // IF SOMETHING IS IN MULTIPLE STUDENT FILES BUT NOT MOST OR ALL...
    if (count > 1 && count < 20) {
      //std::cout << itr->first << " " << count << " : ";
                                                 
      const std::map<std::string,std::vector<Specific> > &has_this_hash = itr->second;
      for (std::map<std::string,std::vector<Specific> >::const_iterator itr2 = has_this_hash.begin();
           itr2 != has_this_hash.end(); itr2++) {
        //std::cout << " " << itr2->first;
        std::string user = itr2->first;
        for (int i = 0; i < itr2->second.size(); i++) {
          similarities[itr2->first].insert(itr2->second[i].position);
        }
      }
      //std::cout << std::endl;
    }
  }


  for (std::map<std::string,std::set<int> >::iterator itr = similarities.begin();
       itr != similarities.end(); itr++) {

    std::cout << "similarities for " << itr->first << " " << itr->second.size() << ":";
    for (std::set<int>::iterator itr2 = itr->second.begin(); itr2 != itr->second.end(); itr2++) {
      std::cout << " " << *itr2;
    }
    std::cout << std::endl;
  }

  
  std::cout << "done" << std::endl;
  
}
