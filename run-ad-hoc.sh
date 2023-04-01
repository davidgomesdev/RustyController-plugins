#!/usr/bin/env bash

ERROR=$(tput setaf 1)
SUCCESS=$(tput setaf 2)
INFO=$(tput setaf 6)
RESET=$(tput sgr0)

LOGS_BASE_DIRECTORY="/var/log/rusty-controller/plugins"
CRON_LOGS_DIRECTORY="$LOGS_BASE_DIRECTORY/cron"
PLUGIN_LOGS_DIRECTORY="$LOGS_BASE_DIRECTORY"

plugin="$1"

if [ ! -d "$plugin" ]; then
  echo "${ERROR}The plugin '$plugin' does not exist!$RESET"
  exit 1
fi

cd "$plugin" || exit 1

if [ ! -f .ad-hoc ]; then
  echo "${ERROR}The plugin '$plugin' is not ad-hoc!$RESET"
  exit 1
fi

mkdir -p "$CRON_LOGS_DIRECTORY"
mkdir -p "$PLUGIN_LOGS_DIRECTORY"

python3 -m venv env && source env/bin/activate && pip install -r requirements.txt | tee -a "$CRON_LOGS_DIRECTORY/$plugin.log"

echo "${INFO}Running '$plugin'...$RESET" | tee -a "$CRON_LOGS_DIRECTORY/$plugin.log"

export LOGS_DIRECTORY="$PLUGIN_LOGS_DIRECTORY"
python main.py || (echo "${ERROR}Plugin failed! (check its logs)$RESET" | tee -a "$CRON_LOGS_DIRECTORY/$plugin.log")

echo "${SUCCESS}Plugin finished!$RESET" | tee -a "$CRON_LOGS_DIRECTORY/$plugin.log"
