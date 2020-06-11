#!/bin/bash

if [ ! -e 'Python' ]; then
    python3 -m venv Python
fi

source Python/bin/activate
pip install --upgrade pip
pip install --upgrade pylint

python -E setup.py install
