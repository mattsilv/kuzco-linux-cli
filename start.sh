#!/bin/bash

# Load config from file if it exists
CONFIG_FILE="config.env"
if [ -f "$CONFIG_FILE" ]; then
  source "$CONFIG_FILE"
else
  # Check for required environment variables
  if [ -z "$WORKER_ID" ] || [ -z "$CODE" ]; then
    echo "Environment variables WORKER_ID and CODE must be set."
    exit 1
  fi
fi

# Parse flags
while getopts "m:s:" opt; do
  case $opt in
    m) MODE=$OPTARG ;;
    s) SESSIONS=$OPTARG ;;
    \?) echo "Invalid option -$OPTARG" >&2; exit 1 ;;
  esac
done

# Define the command to run
COMMAND="kuzco worker start --worker $WORKER_ID --code $CODE"

# Function to kill all tmux sessions
kill_tmux_sessions() {
  tmux list-sessions -F "#{session_name}" | grep '^worker[0-9]\+$' | xargs -I {} tmux kill-session -t {}
}

# Function to count existing tmux sessions
count_existing_sessions() {
  tmux list-sessions -F "#{session_name}" | grep '^worker[0-9]\+$' | wc -l
}

# Fresh start
if [ "$MODE" == "fresh" ]; then
  kill_tmux_sessions
  echo "Stopped all existing tmux sessions."
  START_INDEX=1
else
  START_INDEX=$(count_existing_sessions)
  START_INDEX=$((START_INDEX + 1))
fi

# Start tmux sessions
for i in $(seq $START_INDEX $((START_INDEX + SESSIONS - 1))); do
  tmux new-session -d -s worker$i "$COMMAND"
done

echo "Started $SESSIONS kuzco workers in parallel tmux sessions."