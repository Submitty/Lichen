#!/usr/bin/env bash

mkdir -p /usr/local/submitty/GIT_CHECKOUT/Lichen/
cp -r * /usr/local/submitty/GIT_CHECKOUT/Lichen/

mkdir -p /usr/local/submitty/Lichen/

bash /usr/local/submitty/GIT_CHECKOUT/Lichen/install_lichen.sh
