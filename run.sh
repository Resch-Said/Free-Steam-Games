#!/bin/bash

git pull
python3 -m pip install -r requirements.txt
cd src
python3 main.py