#!/usr/bin/env bash

# Colors

ERROR=$(tput setaf 1)
SUCCESS=$(tput setaf 2)
INFO=$(tput setaf 6)
FINISH=$(tput setaf 30)
RESET=$(tput sgr0)

echo "Killing old session..."
tmux kill-session -t "RustyController plugins" 2>/dev/null && echo "Killed existing tmux session"
tmux new-session -d -s "RustyController plugins" -c "$(pwd)"

BASE_DIR="$PWD"
LOGS_DIR="/var/log/rusty-controller/plugins"

# Don't fail if the current common build fails, there may be a previous build
(./build_common.sh)

find . -mindepth 1 -maxdepth 1 -type d -print0 | while IFS= read -r -d '' dir; do
  cd "$dir" || continue

  wkdir="$PWD"
  plugin="${PWD##*/}"

  if [ -f main.py ]; then
    if [ -f .ad-hoc ]; then
      echo "Ignoring $plugin because it's an ad-hoc plugin."
      cd "$BASE_DIR" || echo "Huh..? Failed to cd to base dir"
      continue
    fi

    echo "${INFO}Running $plugin$RESET"

    mkdir -p "$LOGS_DIR"

    python_command="python3 -m venv env && source env/bin/activate && pip install -r requirements.txt 1>/dev/null; export LOGS_DIRECTORY='$LOGS_DIR'; python3 main.py 2>&1 1>/dev/null > '$LOGS_DIR/$plugin.log' || echo 'Failed running $plugin'"
    tmux new-window -t "RustyController plugins" -n "$plugin" "cd $wkdir && $python_command" && echo "${SUCCESS}Success.$RESET" || echo "${ERROR}Failed!$RESET"
  else
    echo "Ignoring $plugin folder (not a plugin)"
  fi

  cd "$BASE_DIR" || echo "${ERROR}Huh..? Failed to cd to base dir$RESET"
done

echo "${FINISH}Finished RustyController plugins$RESET"
