#!/bin/bash
cd "$(dirname "$0")"

git pull

bash setup.sh
pip3 install -r raspberry_pi_requirements.txt

export GOOGLE_APPLICATION_CREDENTIALS='/home/pi/service_account.json'

python3 webcam_to_pubsub.py
