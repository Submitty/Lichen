#!/usr/bin/env bash

lichen_repository_dir=/usr/local/submitty/GIT_CHECKOUT/Lichen/
lichen_installation_dir=/usr/local/submitty/Lichen/
lichen_data_dir=/var/local/submitty/courses/

# make a simulated GIT_CHECKOUT directory
mkdir -p $lichen_repository_dir
cp -r * $lichen_repository_dir
cd $lichen_repository_dir

# Set up docker in advance
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli

# install Lichen
mkdir -p $lichen_installation_dir
bash $lichen_repository_dir/install_lichen.sh
