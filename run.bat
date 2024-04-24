@echo off

git pull
python -m pip install -r requirements.txt
cd src
python main.py