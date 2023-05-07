#!/usr/bin/env bash

# this script must be run by root or sudo
if [[ "$UID" -ne "0" ]] ; then
    echo "ERROR: This script must be run by root or sudo"
    exit 1
fi

echo -e "Installing lichen... "

lichen_repository_dir=/usr/local/submitty/GIT_CHECKOUT/Lichen
lichen_installation_dir=/usr/local/submitty/Lichen
lichen_vendor_dir=/usr/local/submitty/Lichen/vendor

rm -rf "$lichen_installation_dir"
mkdir "$lichen_installation_dir"
cp -r "$lichen_repository_dir"/* "$lichen_installation_dir"

####################################################################################################
# install C++ dependencies

apt-get update
apt-get install -y clang-6.0 libboost-all-dev

####################################################################################################
# Install Python Dependencies locally (for concatenation)
pip install -r "${lichen_repository_dir}/requirements.txt"

# These permissions changes are copied from Submitty/.setup/INSTALL_SUBMITTY_HELPER.sh
# Setting the permissions are necessary as pip uses the umask of the user/system, which
# affects the other permissions (which ideally should be o+rx, but Submitty sets it to o-rwx).
# This gets run here in case we make any python package changes.
find /usr/local/lib/python*/dist-packages -type d -exec chmod 755 {} +
find /usr/local/lib/python*/dist-packages -type f -exec chmod 755 {} +
find /usr/local/lib/python*/dist-packages -type f -name '*.py*' -exec chmod 644 {} +
find /usr/local/lib/python*/dist-packages -type f -name '*.pth' -exec chmod 644 {} +

####################################################################################################
# get tools/source code from vendor repositories

mkdir -p "${lichen_vendor_dir}/nlohmann"

NLOHMANN_JSON_VERSION=3.9.1

echo "Checking for nlohmann/json: ${NLOHMANN_JSON_VERSION}"

if [ -f "${lichen_vendor_dir}/nlohmann/json.hpp" ] && head -n 10 "${lichen_vendor_dir}/nlohmann/json.hpp" | grep -q "version ${NLOHMANN_JSON_VERSION}"; then
    echo "  already installed"
else
    echo "  downloading"
    wget -O "${lichen_vendor_dir}/nlohmann/json.hpp" "https://github.com/nlohmann/json/releases/download/v${NLOHMANN_JSON_VERSION}/json.hpp" > /dev/null
fi

####################################################################################################
# compile & install the hash comparison tool

pushd "${lichen_installation_dir}/compare_hashes" > /dev/null
cmake "$lichen_repository_dir/compare_hashes"
cmake --build .
if [ "$?" -ne 0 ]; then
    echo -e "ERROR: FAILED TO BUILD HASH COMPARISON TOOL\n"
    exit 1
fi
popd > /dev/null

####################################################################################################
# pull or build Lichen Docker image

if [[ "$#" -ge 1 && "$1" == "build" ]]; then
    docker build -t submitty/lichen "$lichen_repository_dir"
else
    docker pull submitty/lichen:latest
    docker tag submitty/lichen:latest lichen
fi

#####################################################################################################
# fix permissions
chown -R root:root ${lichen_installation_dir}
chmod -R 755 ${lichen_installation_dir}

echo "done"
