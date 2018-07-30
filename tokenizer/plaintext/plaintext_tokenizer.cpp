#include <iostream>
#include <fstream>
#include <string>
#include <cassert>
#include <iomanip>
#include <ctype.h>
#include <cstdio>
#include "nlohmann/json.hpp"

void usage(const std::string &program) {
  std::cerr << "Usage: " << program << " [--ignore_punctuation] [--to_lower] [--ignore_numbers] [--ignore_newlines] < INPUT_FILE.txt > OUTPUT_FILE.json" << std::endl;
  exit(0);
}


int main(int argc, char* argv[]) {

  // ------------------------------
  // handle arguments
  bool ignore_punctuation = false;
  bool to_lower = false;
  bool ignore_numbers = false;
  bool ignore_newlines = false;
  for (int i = 1; i < argc; i++) {
    if (std::string(argv[i]) == std::string("--ignore_punctuation")) {
      ignore_punctuation = true;
    } else if (std::string(argv[i]) == std::string("--to_lower")) {
      to_lower = true;
    } else if (std::string(argv[i]) == std::string("--ignore_numbers")) {
      ignore_numbers = true;
    } else if (std::string(argv[i]) == std::string("--ignore_newlines")) {
      ignore_newlines = true;
    } else {
      std::cerr << "ERROR: Unknown option '" << argv[i] << "'" << std::endl;
      usage(argv[0]);
    }
  }

  // ------------------------------
  // helper variables
  nlohmann::json tokens;
  char c;
  std::string token;
  int row = 1;
  int col = 1;
  int start_row = -1;
  int start_col = -1;
  bool last_was_alpha = false;
  bool last_was_digit = false;

  // ------------------------------
  // loop to read the input file file
  while (std::cin >> std::noskipws >> c) {
    bool is_punctuation = !isspace(c) && !std::isdigit(c) && !std::isalpha(c);

    if ((unsigned int)(c) > 127) {
      // FIXME: for now, just skip utf-8 characters since nlohmann dump gets stuck
      continue;
    }

    // ------------------------------
    // decide when to break the current string
    // break on spaces, punctuation (any symbol), or if we switch between letters and numbers
    if (isspace(c) ||
        is_punctuation ||
        (last_was_alpha && std::isdigit(c)) ||
        (last_was_digit && std::isalpha(c))) {
      if (token != "") {
        // save this token!
        std::map<std::string,nlohmann::json> tmp;
        tmp["line"]=start_row;
        tmp["char"]=start_col;
        if (last_was_digit) {
          assert (!last_was_alpha);
          tmp["type"]="number";
          tmp["value"]=std::stoi(token);
        } else {
          assert (last_was_alpha);
          tmp["type"]="string";
          tmp["value"]=token;
        }
        tokens.push_back(tmp);
        token="";
        last_was_alpha = false;
        last_was_digit = false;
      }
    }

    // ------------------------------
    // decide whether to add this character to the current string
    if (isspace(c)) {
      // never add spaces
    }
    // ------------------------------
    else if (is_punctuation) {
      assert (token == "");
      assert (last_was_alpha == false);
      assert (last_was_digit == false);
      // only add punctuation if its not being ignored
      // (punctuation is always a single symbol character per token)
      if (!ignore_punctuation) {
        std::map<std::string,nlohmann::json> tmp;
        tmp["line"]=row;
        tmp["char"]=col;
        tmp["type"]="punctuation";
        tmp["value"]=std::string(1,c);
        tokens.push_back(tmp);
      }
    }
    // ------------------------------
    else if (std::isdigit(c)) {
      assert (last_was_alpha == false);
      // only add digits/numbers if they are not being ignored
      // numbers will be 1 or more digits 0-9.
      // We break tokens between letters & numbers.
      if (!ignore_numbers) {
        if (token=="") {
          start_row = row;
          start_col = col;
          last_was_digit=true;
        } else {
          assert (last_was_digit == true);
        }
        token.push_back(c);
      }
    }
    // ------------------------------
    else if (isalpha(c)) {
      assert (last_was_digit == false);
      // string tokens will be 1 or more letters a-z or A-Z
      if (token=="") {
        start_row = row;
        start_col = col;
        last_was_alpha=true;
      } else {
        assert (last_was_alpha == true);
      }
      // option to lowercase
      if (to_lower) {
        c = std::tolower(c);
      }
      token.push_back(c);
    }

    // ------------------------------
    if (c == '\n') {
      // advance to the next row/line
      assert (token=="");
      if (!ignore_newlines) {
        // output a token for the newline
        std::map<std::string,nlohmann::json> tmp;
        tmp["line"]=row;
        tmp["char"]=col;
        tmp["type"]="newline";
        tmp["value"]="\n";
        tokens.push_back(tmp);
      }
      row++;
      col=1;
    } else {
      // advance to the next column/character
      col++;
    }
  } 

  // ------------------------------
  if (token != "") {
    // save the last token (if there was no space or newline at the end of the file)
    std::map<std::string,nlohmann::json> tmp;
    tmp["line"]=start_row;
    tmp["char"]=start_col;
    if (last_was_digit) {
      assert (!last_was_alpha);
      tmp["type"]="number";
      tmp["value"]=std::stoi(token);
    } else {
      assert (last_was_alpha);
      tmp["type"]="string";
      tmp["value"]=token;
    }
    tokens.push_back(tmp);
  }

  // ------------------------------
  // export/save in json format
  std::cout << tokens.dump(4) << std::endl;
}
