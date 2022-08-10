#!/bin/sh

KILL_ERROR_MESSAGE="
* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
* An error occured while running Lichen. Your run was probably killed for       *
* exceeding the configured resource limits. Before rerunning, perhaps try any   *
* of the following edits to the configuration:                                  *
* - Increasing the hash size                                                    *
* - Using only active version                                                   *
* - Decreasing the common code threshold                                        *
* - Selecting fewer files to be compared                                        *
* - Comparing against fewer other gradeables                                    *
* - Uploading provided code files                                               *
* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
";

python3 /Lichen/tokenizer/tokenize_all.py                "/data" || exit 1
python3 /Lichen/hasher/hash_all.py                       "/data" || exit 1
/Lichen/compare_hashes/compare_hashes.out                "/data" || { echo "${KILL_ERROR_MESSAGE}"; exit 1; } 
python3 /Lichen/similarity_ranking/similarity_ranking.py "/data";
