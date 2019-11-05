#!/bin/bash

set -e # exit immediately if a command exists with non-zero status
echo $@

echo 'Starting entrypoint...'
echo "Running job: ${1}" # gets first argument
echo "Arguments: ${@:2}" # slices with offset = 2

Rscript scripts/${1}.r "${@:2}" # propogate arguments

echo "End entrypoint."