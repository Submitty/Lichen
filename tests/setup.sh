#!/usr/bin/env bash

lichen_repository_dir=/usr/local/submitty/GIT_CHECKOUT/Lichen/
lichen_installation_dir=/usr/local/submitty/Lichen/
lichen_data_dir=/var/local/submitty/courses/

# make a simulated GIT_CHECKOUT directory
mkdir -p $lichen_repository_dir
cp -r * $lichen_repository_dir
cd $lichen_repository_dir

# install Lichen
mkdir -p $lichen_installation_dir
bash $lichen_repository_dir/install_lichen.sh

# SETUP TOKENIZER TESTS ########################################################
tokenizer_tests_course=$lichen_data_dir/f21/test_tokenizers/lichen/
# make a simulated lichen path for the test_tokenizers course
mkdir -p $tokenizer_tests_course

# set up file structure for plaintext tokenizer tests
# (doesn't need a full file structure, just a place to put files)
mkdir -p $tokenizer_tests_course/plaintext_tokenizer_tests/
