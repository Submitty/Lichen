#!/usr/bin/env bash

########################################################################################################################
########################################################################################################################
# this script must be run by root or sudo
if [[ "$UID" -ne "0" ]] ; then
    echo "ERROR: This script must be run by root or sudo"
    exit 1
fi

# requires 2 arguments
if [[ "$#" -ne 2 ]]; then
    echo -e "Usage:"
    echo -e "   " $0 " <LICHEN_REPOSITORY_DIR> <LICHEN_INSTALL_DIR>"
    exit 1
fi

lichen_repository_dir=$1
lichen_installation_dir=$2

echo -e "Installing lichen... "

nlohmann_dir=${lichen_repository_dir}../vendor/nlohmann/json/


########################################################################################################################
# get tools/source code from other repositories
if [ ! -d "${nlohmann_dir}" ]; then
    echo 'should install'
    git clone --depth 1 https://github.com/nlohmann/json.git ${nlohmann_dir}
fi

mkdir -p ${lichen_installation_dir}/bin


########################################################################################################################
# compile & install the tokenizers

pushd ${lichen_repository_dir}  > /dev/null
clang++ -I ${nlohmann_dir}/include/ -std=c++11 -Wall tokenizer/plaintext/plaintext_tokenizer.cpp -o ${lichen_installation_dir}/bin/plaintext_tokenizer.out
if [ $? -ne 0 ]; then
    echo -e "ERROR: FAILED TO BUILD PLAINTEXT TOKENIZER\n"
    exit 1
fi
popd > /dev/null


# compile & install the hash comparison tool
pushd ${lichen_repository_dir}  > /dev/null
clang++ -I ${nlohmann_dir}/include/ -lboost_system -lboost_filesystem -Wall -g -std=c++11 -Wall compare_hashes/compare_hashes.cpp -o ${lichen_installation_dir}/bin/compare_hashes.out
if [ $? -ne 0 ]; then
    echo -e "ERROR: FAILED TO BUILD HASH COMPARISON TOOL\n"
    exit 1
fi
popd > /dev/null


########################################################################################################################

cp ${lichen_repository_dir}/bin/* ${lichen_installation_dir}/bin/


########################################################################################################################
# fix permissions
chown -R root:root ${lichen_installation_dir}
chmod 755 ${lichen_installation_dir}
chmod 755 ${lichen_installation_dir}/bin
chmod 755 ${lichen_installation_dir}/bin/*

echo "done"


#${bin_location}/plaintext_tokenizer.out                                                                    < tokenizer/plaintext/input.txt > output.json
#${bin_location}/plaintext_tokenizer.out --ignore_newlines                                                  < tokenizer/plaintext/input.txt > output_ignore_newlines.json
#${bin_location}/plaintext_tokenizer.out --to_lower                                                         < tokenizer/plaintext/input.txt > output_to_lower.json
#${bin_location}/plaintext_tokenizer.out --ignore_punctuation                                               < tokenizer/plaintext/input.txt > output_ignore_punctuation.json
#${bin_location}/plaintext_tokenizer.out --ignore_punctuation --ignore_numbers --ignore_newlines --to_lower < tokenizer/plaintext/input.txt > output_ignore_everything.json



