#!/bin/bash
cd "$(dirname "$0")"

git pull

setup.sh
pip3 install -r raspberry_pi_requirements.txt

python3 webcam_to_pubsub.py