#!/bin/bash

if [ ! -d "./env" ]
then
    echo "Virtual env does not exists. "
    echo "Installing packages... "
    sudo apt-get update
    sudo apt-get -y upgrade
    sudo apt-get -y install libcblas-dev
    sudo apt-get -y install libhdf5-dev
    sudo apt-get -y install libhdf5-serial-dev
    sudo apt-get -y install libatlas-base-dev
    sudo apt-get -y install libjasper-dev 
    sudo apt-get -y install libqtgui4 
    sudo apt-get -y install libqt4-test
    python3 -m pip install --upgrade pip
    python3 -m pip install --user virtualenv
    python3 -m venv env
    source ./env/bin/activate
    python3 -m pip install -r requirements.txt
    mkdir ./detection_video
    mkdir ./motion_video
else
    source ./env/bin/activate
fi

python ./app.py --sms 1 --save 1 --detection 1 --nightsave 1 & python ./keep_alive.py
