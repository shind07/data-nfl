FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive 

RUN apt-get update && \
    apt-get install -y  \
        python3 \ 
        python3-pip \
        git \
        r-base && \
    apt-get clean

COPY requirements.txt /tmp/requirements.txt

RUN pip3 install -r tmp/requirements.txt

# RUN git clone https://github.com/maksimhorowitz/nflscrapR.git nflscrapr

COPY . /app

WORKDIR /app

CMD python3 jobs/play_by_play.py

# ENTRYPOINT bash entrypoint.sh