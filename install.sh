#!/usr/bin/env bash

src_location="."
build_location="."
bin_location="./bin"

nlohmann_dir=${src_location}/GIT_NLOHMANN_JSON/

if [ ! -d "${nlohmann_dir}" ]; then
    echo 'should install'
    git clone --depth 1 https://github.com/nlohmann/json.git ${nlohmann_dir}
fi


mkdir -p ${bin_location}
clang++ -I ${nlohmann_dir}/include/ -std=c++11 -Wall tokenizer/plaintext/plaintext_tokenizer.cpp -o ${bin_location}/plaintext_tokenizer.out

${bin_location}/plaintext_tokenizer.out                                                                    < tokenizer/plaintext/input.txt > output.json
${bin_location}/plaintext_tokenizer.out --ignore_newlines                                                  < tokenizer/plaintext/input.txt > output_ignore_newlines.json
${bin_location}/plaintext_tokenizer.out --to_lower                                                         < tokenizer/plaintext/input.txt > output_to_lower.json
${bin_location}/plaintext_tokenizer.out --ignore_punctuation                                               < tokenizer/plaintext/input.txt > output_ignore_punctuation.json
${bin_location}/plaintext_tokenizer.out --ignore_punctuation --ignore_numbers --ignore_newlines --to_lower < tokenizer/plaintext/input.txt > output_ignore_everything.json



