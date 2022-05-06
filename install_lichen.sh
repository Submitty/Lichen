#!/usr/bin/env bash

# this script must be run by root or sudo
if [[ "$UID" -ne "0" ]] ; then
    echo "ERROR: This script must be run by root or sudo"
    exit 1
fi

echo -e "Installing lichen... "

lichen_repository_dir=/usr/local/submitty/GIT_CHECKOUT/Lichen
lichen_installation_dir=/usr/local/submitty/Lichen

cp -r "$lichen_repository_dir"/* "$lichen_installation_dir"

docker build -t lichen "$lichen_repository_dir"

# fix permissions
chown -R root:root ${lichen_installation_dir}
chmod -R 755 ${lichen_installation_dir}

echo "done"
