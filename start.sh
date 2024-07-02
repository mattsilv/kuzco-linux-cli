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

# Default values
MODE="fresh"
SESSIONS=5
WAIT_TIME=5
RETRY_COUNT=3

# Parse flags
while getopts "m:s:w:r:" opt; do
  case $opt in
    m) MODE=$OPTARG ;;
    s) SESSIONS=$OPTARG ;;
    w) WAIT_TIME=$OPTARG ;;
    r) RETRY_COUNT=$OPTARG ;;
    \?) echo "Invalid option -$OPTARG" >&2; exit 1 ;;
  esac
done

# Ensure tmux server is running
if ! tmux list-sessions >/dev/null 2>&1; then
  echo "Starting tmux server..."
  tmux start-server
fi

# Define the command to run
COMMAND="kuzco worker start --worker $WORKER_ID --code $CODE"

# Function to kill all tmux sessions
kill_tmux_sessions() {
  tmux list-sessions -F "#{session_name}" | grep '^worker[0-9]\+$' | xargs -I {} tmux kill-session -t {}
}

# Function to check if a session exists
session_exists() {
  tmux has-session -t "$1" 2>/dev/null
}

# Fresh start
if [ "$MODE" == "fresh" ]; then
  kill_tmux_sessions
  echo "Stopped all existing tmux sessions."
  START_INDEX=1
else
  START_INDEX=$(tmux list-sessions -F "#{session_name}" | grep '^worker[0-9]\+$' | wc -l)
  START_INDEX=$((START_INDEX + 1))
fi

# Start tmux sessions with a wait time and logging
for i in $(seq $START_INDEX $((START_INDEX + SESSIONS - 1))); do
  LOG_FILE="worker$i.log"
  # Truncate the log file to a maximum size of 1MB
  if [ -f "$LOG_FILE" ]; then
    truncate -s 1M "$LOG_FILE"
  fi
  SUCCESS=false
  for ((j=1; j<=RETRY_COUNT; j++)); do
    if session_exists "worker$i"; then
      tmux kill-session -t "worker$i"
    fi
    tmux new-session -d -s worker$i bash -c "$COMMAND > >(tee -a $LOG_FILE) 2> >(tee -a $LOG_FILE >&2)"
    if [ $? -eq 0 ]; then
      SUCCESS=true
      break
    else
      echo "Retry $j/$RETRY_COUNT for tmux session worker$i"
    fi
    sleep $WAIT_TIME
  done
  if [ "$SUCCESS" == true ]; then
    echo "Started tmux session worker$i and logging to $LOG_FILE"
  else
    echo "Failed to start tmux session worker$i after $RETRY_COUNT attempts"
  fi
done

echo "Started $SESSIONS kuzco workers in parallel tmux sessions."
