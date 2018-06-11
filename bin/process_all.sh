#!/bin/bash

/usr/local/submitty/Lichen/bin/concatenate_all.py s18 sample grades_released_homework 
/usr/local/submitty/Lichen/bin/tokenize_all.py    s18 sample grades_released_homework  --plaintext
/usr/local/submitty/Lichen/bin/hash_all.py        s18 sample grades_released_homework  --window 10  --plaintext
