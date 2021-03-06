#!/bin/bash
# TODO: why does systemctl restart not work?
parent_path=$(cd `dirname $0` && pwd)

git_pull () {
    git pull
}   

install_requirements () {
    bash setup.sh
    pip3 install -r requirements.txt
}

main () {
    git_pull
    if [[ $1 -eq "install_requirements" ]]
    then
        install_requirements
    fi



    # TODO: Fix this to pick up ADC
    # TODO: Fix local logs
    export GOOGLE_APPLICATION_CREDENTIALS='/home/pi/service_account.json'

    echo "Starting webcam python script."
    python3 webcam_to_pubsub.py > /home/pi/sample_startup.log 2>&1
}

pushd $parent_path

main

popd