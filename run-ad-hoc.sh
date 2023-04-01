#!/usr/bin/env bash

LOGS_DIRECTORY="/var/log/rusty-controller/plugins/$1"

{
  (python3 -m venv env && source env/bin/activate && pip install -r requirements.txt) 2>&1
} 1>/dev/null

mkdir -p "$LOGS_DIRECTORY"

LOGS_DIRECTORY="$LOGS_DIRECTORY"; python main.py
