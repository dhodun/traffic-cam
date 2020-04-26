# traffic-cam

Raspberry Pi Traffic Cam project using GCP to detect / count / classify boats, cars, etc.

## Setup Raspberry Pi

Equipment Used:

* Logitech c930e HD Webcam
* Raspberry Pi 3 B+ (I bought ABOX Complete Starter kit, 32GB)

### Raspberry Pi Setup

ABOX Raspberry Pi 3 B+ Complete Starter Kit with Model B Plus Motherboard 32GB Micro SD Card NOOBS, 5V 3A On/Off Power Supply, Premium Black Case, HDMI Cable, SD Card Reader with USB A&USB C, Heatsink

We're using the `imutils` module to improve performance by running th webcam on another thread. You can read more about using this module and threading to improve performance for [webcams](https://www.pyimagesearch.com/2015/12/21/increasing-webcam-fps-with-python-and-opencv/), [Raspberry Pi cams](https://www.pyimagesearch.com/2015/12/28/increasing-raspberry-pi-fps-with-python-and-opencv/), and [files](https://www.pyimagesearch.com/2017/02/06/faster-video-file-fps-with-cv2-videocapture-and-opencv/).
