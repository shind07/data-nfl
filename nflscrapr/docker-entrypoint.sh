#!/bin/bash

set -e # exit immediately if a command exists with non-zero status

echo 'Starting entrypoint...'
echo "Running test script..."

Rscript scripts/games.r --year="2018" --week=2

echo "Test script ran."
echo "End entrypoint"