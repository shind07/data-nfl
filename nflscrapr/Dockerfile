FROM r-base:3.6.1

ENV DEBIAN_FRONTEND=noninteractive 

RUN apt-get update \
    && apt-get install -y \
        libcurl4-openssl-dev \
        libxml2-dev \
        libssl-dev \
    && apt-get clean

RUN R -e "install.packages('devtools', repos='http://cran.us.r-project.org')"

# need to install this package separately b/c the install w/ nflscrapR fails.
RUN R -e "install.packages('hashmap', repos='http://cran.us.r-project.org')"

RUN R -e "devtools::install_github(repo='maksimhorowitz/nflscrapR')"

# everything above here is cached :) 

COPY scripts tmp/scripts

WORKDIR tmp/scripts

CMD Rscript play_by_play.r