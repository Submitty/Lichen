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
lichen_vendor_dir=/usr/local/submitty/Lichen/vendor


########################################################################################################################
# install dependencies

# install clang
apt-get install -y clang-6.0

# boost
apt-get install -y libboost-all-dev

# python requirements
pip install -r ${lichen_repository_dir}/requirements.txt

########################################################################################################################
# get tools/source code from other repositories

mkdir -p ${lichen_vendor_dir}/nlohmann

NLOHMANN_JSON_VERSION=3.9.1

echo "Checking for nlohmann/json: ${NLOHMANN_JSON_VERSION}"

if [ -f ${lichen_vendor_dir}/nlohmann/json.hpp ] && head -n 10 ${lichen_vendor_dir}/nlohmann/json.hpp | grep -q "version ${NLOHMANN_JSON_VERSION}"; then
    echo "  already installed"
else
    echo "  downloading"
    wget -O ${lichen_vendor_dir}/nlohmann/json.hpp https://github.com/nlohmann/json/releases/download/v${NLOHMANN_JSON_VERSION}/json.hpp > /dev/null
fi

########################################################################################################################
# compile & install the tools

mkdir -p ${lichen_installation_dir}/bin
mkdir -p ${lichen_installation_dir}/tools/assignments

#--------------------
# plaintext tool
pushd ${lichen_repository_dir}  > /dev/null
clang++ -I ${lichen_vendor_dir} -std=c++11 -Wall -O3 tokenizer/plaintext/plaintext_tokenizer.cpp -o ${lichen_installation_dir}/bin/plaintext_tokenizer.out
if [ $? -ne 0 ]; then
    echo -e "ERROR: FAILED TO BUILD PLAINTEXT TOKENIZER\n"
    exit 1
fi
popd > /dev/null


#-------------------------------------------
# compile & install the hash comparison tool
pushd ${lichen_repository_dir}  > /dev/null
clang++ -I ${lichen_vendor_dir} -lboost_system -lboost_filesystem -Wall -Wextra -Werror -g -O3 -flto -funroll-loops -std=c++11 compare_hashes/compare_hashes.cpp -o ${lichen_installation_dir}/bin/compare_hashes.out
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
