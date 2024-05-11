#!/bin/bash

git pull origin dev
python3 -m pip install -r requirements.txt
cd src
python3 main.py