#!/usr/bin/env bash

ERROR=$(tput setaf 1)
SUCCESS=$(tput setaf 2)
INFO=$(tput setaf 6)
RESET=$(tput sgr0)

LOGS_DIRECTORY="/var/log/rusty-controller/plugins/$1"

plugin="$1"

cd "$PLUGIN_NAME" || (echo "${ERROR}The plugin $plugin does not exist!$RESET"; exit 1)

if [ ! -f .ad-hoc ]; then
  echo "${ERROR}The plugin $plugin is not ad-hoc!$RESET"
  exit 1
fi

{
  (python3 -m venv env && source env/bin/activate && pip install -r requirements.txt) 2>&1
} 1>/dev/null

mkdir -p "$LOGS_DIRECTORY"

echo "${INFO}Running $plugin...$RESET"

LOGS_DIRECTORY="$LOGS_DIRECTORY"; python main.py

echo "${SUCCESS}Plugin finished!$RESET"
