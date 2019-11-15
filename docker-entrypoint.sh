set -e # exit immediately if a command exists with non-zero status

echo 'Starting entrypoint...'
$@
echo "End entrypoint."