#!/usr/bin/env sh

# copy this to .git/hooks/pre-commit
# if you want to run check this on each commit/rebase etc...

pylint -j $(nproc) --rcfile=.pylintrc src/logsearch

LINT_EXIT_CODE=$?

echo "pylint exited with status: $LINT_EXIT_CODE"

exit $LINT_EXIT_CODE
