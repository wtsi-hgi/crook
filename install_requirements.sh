#!/usr/bin/env bash

# Sanger venv install as of 21 Dec 2021
/software/hgi/installs/pyenv/versions/3.8.3/bin/python -m venv .venv
source .venv/bin/activate
pip install -U pip setuptools wheel -r requirements.txt
