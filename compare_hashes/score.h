#ifndef SCORE_H
#define SCORE_H

#include <cassert>

typedef int location_in_submission;
typedef unsigned int hash;
typedef std::string user_id;
typedef unsigned int version_number;

// represents the plagiarism score for a given submissions, used for the overall rankings file
class Score {
public:
  // CONSTRUCTOR
  Score(unsigned int hashes_matched, float percent): hashes_matched(hashes_matched), percent(percent), score(-1) {}
  Score(const Score &other) { copy(other); }

  // GETTERS
  float getPercent() const { return percent; }
  unsigned int getHashesMatched() const { return hashes_matched; }

  // MODIFIER
  // Each submission in the ranking file gets a composite score that weighs both its percentage
  // of suspicious matches, and its percentile of total number of hashes matched
  void calculateScore(unsigned int max_hashes_matched) {
    assert(PERCENT_WEIGHT + MATCH_WEIGHT == 1);
    score = PERCENT_WEIGHT*(percent/100.0) + MATCH_WEIGHT*((1.0*hashes_matched)/max_hashes_matched);
  }

  // OPERATORS
  bool operator>(const Score &other_s) const {
    return this->getScore() > other_s.getScore();
  }
  bool operator==(const Score &other_s) const {
    return this->getScore() == other_s.getScore();
  }
  Score& operator=(const Score& other) {
    if (this != &other) {
      copy(other);
    }
    return *this;
  }


private:
  const float PERCENT_WEIGHT = 0.5;
  const float MATCH_WEIGHT = 0.5;
  unsigned int hashes_matched;
  float percent;
  float score;

  void copy(const Score &other) {
    hashes_matched = other.hashes_matched;
    percent = other.percent;
    score = other.score;
  }
  float getScore() const { assert(score >= 0 && score <= 1); return score; }
};

#endif
