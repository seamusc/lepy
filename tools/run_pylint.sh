#!/usr/bin/env sh

pylint -j $(nproc) --rcfile=.pylintrc src/logsearch

echo "pylint exited with status: $?"

exit 0
