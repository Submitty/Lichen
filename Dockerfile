FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive

# C++ and Python
RUN apt-get update \
    && apt-get install -y \
       libboost-all-dev \
       python3.8 \
       python3-pip \
       clang-6.0 \
       default-jdk

# Python Dependencies
COPY requirements.txt /Lichen/requirements.txt
RUN pip install -r /Lichen/requirements.txt

# The script we run on startup
CMD ["/Lichen/bin/process_all.sh"]