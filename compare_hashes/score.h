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
    score = PERCENT_WEIGHT*(percent/100.0) + MATCH_WEIGHT*(static_cast<float>(hashes_matched)/max_hashes_matched);
  }

  // OPERATORS
  bool operator>(const Score &other_s) const {
    constexpr float EPSILON = 0.0001;
    return std::abs(getScore() - other_s.getScore()) > EPSILON && getScore() > other_s.getScore();
  }
  bool operator==(const Score &other_s) const {
    return getScore() == other_s.getScore();
  }
  Score& operator=(const Score& other) {
    if (this != &other) {
      copy(other);
    }
    return *this;
  }


private:
  static constexpr float PERCENT_WEIGHT = 0.5;
  static constexpr float MATCH_WEIGHT = 0.5;
  // just a sanity check to make sure these values are appropriately updated in the future
  static_assert(PERCENT_WEIGHT + MATCH_WEIGHT == 1, "Weights must add to 1");

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
