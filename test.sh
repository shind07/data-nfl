#!/bin/bash

set -e # exit immediately if a command exists with non-zero status

echo 'Starting entrypoint...'
echo $@
echo ${1} # gets first argument
echo ${@:2} # slies with offset = 2

Rscript scripts/${1}.r "${@:2}" # propogate arguments

echo "End entrypoint"