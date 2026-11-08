#!/bin/bash
set -e
cd "$(dirname "$0")/.."

if [ ! -x .venv/bin/python ]; then
    echo "FAIL .venv missing; run util/init.sh"
    exit 1
fi

.venv/bin/python -m unittest discover -s test -v
