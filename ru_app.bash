#!/bin/bash

source ./env/bin/activate

python ./app.py & chromium-browser 192.168.1.126:5000