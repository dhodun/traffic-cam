#!/bin/bash

# Install packages
sudo bash setup.sh

# TODO: seems to run as root?
# TODO: Maybe change to local so you can see the video that it's capturing?
sudo cp ./traffic-cam.service /lib/systemd/system/traffic-cam.service
sudo chmod 644 /lib/systemd/system/traffic-cam.service
sudo systemctl daemon-reload
sudo systemctl enable traffic-cam.service

# sudo reboot
