FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive 

# Need to add-apt-repo so that the latest r version installed, since
# nflscrap r requires r >= 3.5, https://cran.r-project.org/bin/linux/ubuntu/README.html
# add-apt-repo requires the software-properties-common to work
RUN apt-get update \
    && apt-get install -y gnupg2 \
    && apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 51716619E084DAB9 \
    && apt-get install -y software-properties-common \
    && add-apt-repository 'deb https://cloud.r-project.org/bin/linux/ubuntu bionic-cran35/' \ 
    && apt-get install -y r-base \
        libcurl4-openssl-dev \
        libxml2-dev \
        libssl-dev \
    && apt-get clean

# need to install some packages separately b/c the install w/ nflscrapR fails w/o them
RUN R -e "install.packages('devtools', repos='http://cran.us.r-project.org')"
RUN R -e "install.packages('hashmap', repos='http://cran.us.r-project.org')"
RUN R -e "install.packages('optparse')"
RUN R -e "devtools::install_github(repo='maksimhorowitz/nflscrapR')"

RUN apt-get install -y  \
        python3 \ 
        python3-pip \
        git \
    && apt-get clean

COPY requirements.txt /tmp/requirements.txt
RUN pip3 install -r tmp/requirements.txt

COPY docker-entrypoint.sh /usr/local/bin/

COPY . /app
WORKDIR /app

ENTRYPOINT [ "bash", "docker-entrypoint.sh" ]
CMD [ "sleep", "infinity" ]