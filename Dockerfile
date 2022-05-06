FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive

# C++ and Python
RUN apt-get update \
    && apt-get install -y \
       clang \
       llvm \
       libboost-all-dev \
       wget \
       python3.10 \
       python3-pip \
    && mkdir -p /usr/local/submitty/Lichen/vendor/nlohmann/ \
    && wget -O /usr/local/submitty/Lichen/vendor/nlohmann/json.hpp https://github.com/nlohmann/json/releases/download/v3.9.1/json.hpp > /dev/null \
    && rm -rf /var/lib/apt/lists/*

# Python Dependencies
COPY requirements.txt /Lichen/requirements.txt
RUN pip install -r /Lichen/requirements.txt

# Copy and compile the code for compare_hashes
COPY compare_hashes /Lichen/compare_hashes
RUN clang++ -I /usr/local/submitty/Lichen/vendor -lboost_filesystem -lboost_system -Wall -Wextra -Werror -g -Ofast -flto -funroll-loops -std=c++14 /Lichen/compare_hashes/compare_hashes.cpp /Lichen/compare_hashes/submission.cpp -o /Lichen/compare_hashes/compare_hashes.out

# Copy the tokenizers
COPY tokenizer /Lichen/tokenizer

# Copy the hasher
COPY hasher /Lichen/hasher

# Copy the similarity ranking system
COPY similarity_ranking /Lichen/similarity_ranking

# Copy necessary things from /bin
COPY bin/lichen_config.json /Lichen/bin/lichen_config.json
COPY bin/process_all.sh /Lichen/bin/process_all.sh

# Fix permissions
RUN chmod +x /Lichen/bin/process_all.sh \
    && chmod +x /Lichen/tokenizer/tokenize_all.py \
    && chmod +x /Lichen/hasher/hash_all.py \
    && chmod +x /Lichen/similarity_ranking/similarity_ranking.py

# The script we run on startup
CMD ["/Lichen/bin/process_all.sh"]