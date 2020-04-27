#!/bin/bash

sudo cp ./traffic_cam.service /lib/systemd/system/traffic_cam.service
sudo chmod 644 /lib/systemd/system/traffic_cam.service
sudo systemctl daemon-reload
sudo systemctl enable traffic_cam.service

# sudo reboot