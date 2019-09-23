FROM r-base

COPY install.r tmp/install.r
RUN ["Rscript", "tmp/install.r"]

COPY . /usr/local/src/myscripts
WORKDIR /usr/local/src/myscripts

ENTRYPOINT [ "bash", "entrypoint.sh" ]