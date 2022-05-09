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

# Install Python Dependencies locally (for concatenation)
pip install -r /Lichen/requirements.txt

# These permissions changes are copied from Submitty/.setup/INSTALL_SUBMITTY_HELPER.sh
# Setting the permissions are necessary as pip uses the umask of the user/system, which
# affects the other permissions (which ideally should be o+rx, but Submitty sets it to o-rwx).
# This gets run here in case we make any python package changes.
find /usr/local/lib/python*/dist-packages -type d -exec chmod 755 {} +
find /usr/local/lib/python*/dist-packages -type f -exec chmod 755 {} +
find /usr/local/lib/python*/dist-packages -type f -name '*.py*' -exec chmod 644 {} +
find /usr/local/lib/python*/dist-packages -type f -name '*.pth' -exec chmod 644 {} +

# Create the Docker container
docker build -t lichen "$lichen_repository_dir"

# fix permissions
chown -R root:root ${lichen_installation_dir}
chmod -R 755 ${lichen_installation_dir}

echo "done"
