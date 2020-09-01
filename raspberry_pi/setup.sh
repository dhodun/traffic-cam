#!/bin/bash

# install prerequisites for opencv
sudo apt-get update
sudo apt-get -y install libhdf5-dev libhdf5-serial-dev libhdf5-103
sudo apt-get -y install libqtgui4 libqtwebkit4 libqt4-test python3-pyqt5
sudo apt-get -y install libatlas-base-dev
sudo apt-get -y install libjasper-dev
sudo apt-get -y upgrade