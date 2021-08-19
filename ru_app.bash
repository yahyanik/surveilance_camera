#!/bin/bash

if [ ! -d "./env" ]
then
    echo "Virtual env does not exists. "
    echo "Installing packages... "
    python3 -m pip install --user virtualenv
    python3 -m venv env
    source ./env/bin/activate
    python3 -m pip install -r requirements.txt
    mkdir ./detection_video
    mkdir ./motion_video
else
    source ./env/bin/activate
fi

python ./app.py & chromium-browser 192.168.1.126:811
