FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive 

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y  \
        python3 \ 
        python3-pip \
        git \
        r-base && \
    apt-get clean

COPY ./requirements.txt ./tmp/requirements.txt

RUN pip3 install -r tmp/requirements.txt

CMD python3 --version


