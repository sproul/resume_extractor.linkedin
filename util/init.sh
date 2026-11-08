#!/bin/bash
set -e
cd "$(dirname "$0")/.."

if [ ! -x .venv/bin/python ]; then
    python3 -m venv .venv
    echo "OK created .venv"
else
    echo "OK .venv already present"
fi

.venv/bin/python -m pip install -e . >/dev/null
echo "OK installed dependencies"

if [ -f "$HOME/.linkedin" ]; then
    chmod 600 "$HOME/.linkedin"
    echo "OK secured $HOME/.linkedin"
fi

echo "OK init done"
