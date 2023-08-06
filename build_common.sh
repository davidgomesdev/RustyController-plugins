#!/usr/bin/env bash

# Colors

INFO=$(tput setaf 6)
RESET=$(tput sgr0)

LOGS_DIR="/var/log/rusty-controller/plugins"

echo "${INFO}Building common wheel$RESET"
cd common || exit 1

# Don't fail if the requirements aren't successfully installed, because there might be some successfully cached ones
python3 -m venv env && source env/bin/activate && pip install -r requirements.txt 1>/dev/null

# The full name of the wheel is required
rm -rf dist/; python3 -m build --wheel > "$LOGS_DIR/common.log" || exit 1

cd ..
