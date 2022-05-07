#!/usr/bin/env bash

lichen_repository_dir=/usr/local/submitty/GIT_CHECKOUT/Lichen/
lichen_installation_dir=/usr/local/submitty/Lichen/

# make a simulated GIT_CHECKOUT directory
mkdir -p "$lichen_repository_dir"
cp -r * "$lichen_repository_dir"
cd "$lichen_repository_dir"

# Install Python dependencies for unit tests
pip install -r "$lichen_repository_dir"/requirements.txt

# Setup docker
sudo apt-get update
apt-get install ca-certificates curl gnupg lsb-release

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli

# install Lichen
mkdir -p "$lichen_installation_dir"
bash "$lichen_repository_dir"/install_lichen.sh
