#!/bin/bash
git pull

setup.sh
pip3 install -r raspberry_pi_requirements.txt

python3 pipeline.py