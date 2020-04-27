#!/bin/bash
cd "$(dirname "$0")"

git pull

bash setup.sh
pip3 install -r raspberry_pi_requirements.txt

# TODO: Fix this to pick up ADC
export GOOGLE_APPLICATION_CREDENTIALS='/home/pi/service_account.json'

python3 webcam_to_pubsub.py > /home/pi/sample_startup.log 2>&1
