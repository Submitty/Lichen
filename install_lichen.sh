#!/usr/bin/env bash

########################################################################################################################
########################################################################################################################
# this script must be run by root or sudo
if [[ "$UID" -ne "0" ]] ; then
    echo "ERROR: This script must be run by root or sudo"
    exit 1
fi

echo -e "Installing lichen... "

lichen_repository_dir=/usr/local/submitty/GIT_CHECKOUT/Lichen
lichen_installation_dir=/usr/local/submitty/Lichen

nlohmann_dir=${lichen_repository_dir}/../vendor/nlohmann/json


########################################################################################################################
# install dependencies

# install clang
apt-get install clang-6.0

# boost
apt-get install libboost-all-dev

# python requirements
pip install -r requirements.txt

########################################################################################################################
# get tools/source code from other repositories

if [ ! -e "${nlohmann_dir}" ]; then
    echo "Check out the vendor nlohmann/json repository"
    mkdir -p nlohmann_dir
    git clone --depth 1 https://github.com/nlohmann/json.git ${nlohmann_dir}
fi


########################################################################################################################
# compile & install the tools

mkdir -p ${lichen_installation_dir}/bin
mkdir -p ${lichen_installation_dir}/tools/assignments

#--------------------
# plaintext tool
pushd ${lichen_repository_dir}  > /dev/null
clang++ -I ${nlohmann_dir}/include/ -std=c++11 -Wall tokenizer/plaintext/plaintext_tokenizer.cpp -o ${lichen_installation_dir}/bin/plaintext_tokenizer.out
if [ $? -ne 0 ]; then
    echo -e "ERROR: FAILED TO BUILD PLAINTEXT TOKENIZER\n"
    exit 1
fi
popd > /dev/null


#-------------------------------------------
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

cp ${lichen_repository_dir}/tokenizer/c/c_tokenizer.py ${lichen_installation_dir}/bin/c_tokenizer.py
cp ${lichen_repository_dir}/tokenizer/python/python_tokenizer.py ${lichen_installation_dir}/bin/python_tokenizer.py
cp ${lichen_repository_dir}/tokenizer/java/java_tokenizer.py ${lichen_installation_dir}/bin/java_tokenizer.py
cp ${lichen_repository_dir}/tokenizer/mips/mips_tokenizer.py ${lichen_installation_dir}/bin/mips_tokenizer.py
cp ${lichen_repository_dir}/tokenizer/data.json ${lichen_installation_dir}/bin/data.json

cp -rf ${lichen_repository_dir}/tools/* ${lichen_installation_dir}/tools

########################################################################################################################
# fix permissions
chown -R root:root ${lichen_installation_dir}
chmod 755 ${lichen_installation_dir}
chmod 755 ${lichen_installation_dir}/bin
chmod 755 ${lichen_installation_dir}/bin/*

echo "done"
