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

# Don't fail if the current common build fails, there may be a previous build
(./build_common.sh)

cd "$plugin" || exit 1

if [ ! -f .ad-hoc ]; then
  echo "${ERROR}The plugin '$plugin' is not ad-hoc!$RESET"
  exit 1
fi

mkdir -p "$CRON_LOGS_DIRECTORY"
mkdir -p "$PLUGIN_LOGS_DIRECTORY"

echo "${INFO} --- Installing dependencies... --- $RESET" | tee -a "$CRON_LOGS_DIRECTORY/$plugin.log"

python3 -m venv env && source env/bin/activate && pip install -r requirements.txt 2>&1 1>/dev/null | tee -a "$CRON_LOGS_DIRECTORY/$plugin.log"
pip install --upgrade --force-reinstall --no-deps ../common/dist/common-1.0-py3-none-any.whl

echo "${INFO} --- Running... --- $RESET" | tee -a "$CRON_LOGS_DIRECTORY/$plugin.log"

export LOGS_DIRECTORY="$PLUGIN_LOGS_DIRECTORY"
(python main.py 2>&1 1>/dev/null || echo "${ERROR}* Plugin failed! *$RESET") | tee -a "$CRON_LOGS_DIRECTORY/$plugin.log"

echo "${SUCCESS} --- Plugin completed --- $RESET" | tee -a "$CRON_LOGS_DIRECTORY/$plugin.log"
