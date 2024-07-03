# File: tmux_manager.py

import subprocess
import time
import os
import traceback
from functools import wraps
import threading
from logger import tmux_logger as logger
from health_check import health_check

def retry_with_backoff(retries=3, backoff_in_seconds=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            x = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if x == retries:
                        raise
                    else:
                        logger.warning(f"Attempt {x + 1} failed: {str(e)}")
                        time.sleep(backoff_in_seconds * 2 ** x)
                        x += 1
        return wrapper
    return decorator

def session_exists(session_name):
    logger.debug(f"Checking if session '{session_name}' exists")
    result = subprocess.run(['tmux', 'has-session', '-t', session_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    exists = result.returncode == 0
    logger.debug(f"Session '{session_name}' exists: {exists}")
    return exists

def kill_session(session_name):
    logger.info(f"Killing session '{session_name}'")
    try:
        subprocess.run(['tmux', 'kill-session', '-t', session_name], check=True, capture_output=True)
        logger.debug(f"Successfully killed session '{session_name}'")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to kill session '{session_name}': {e.stderr.decode().strip()}")

@retry_with_backoff(retries=3, backoff_in_seconds=2)
def start_session(session_name, command, log_file):
    logger.info(f"Starting session '{session_name}'")
    full_command = f'bash -c "{{ {command}; }} > {log_file} 2>&1 || {{ echo \\"Error occurred:\\" >&2; cat {log_file} >&2; }}"'
    try:
        subprocess.run(['tmux', 'new-session', '-d', '-s', session_name, full_command], check=True, capture_output=True)
        logger.debug(f"Successfully started session '{session_name}'")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start session '{session_name}': {e.stderr.decode().strip()}")
        logger.error(f"Command output: {e.stdout.decode().strip()}")
        logger.error(f"Error traceback: {traceback.format_exc()}")
        raise

def manage_sessions(config, mode='fresh', sessions=5, wait_time=5, retry_count=3):
    worker_command = f'kuzco worker start --worker {config["WORKER_ID"]} --code {config["CODE"]}'
    logger.info(f"Managing sessions: mode={mode}, sessions={sessions}, wait_time={wait_time}, retry_count={retry_count}")

    if mode == 'fresh':
        logger.info("Fresh mode: Stopping all existing tmux sessions")
        try:
            result = subprocess.run(['tmux', 'list-sessions'], capture_output=True, text=True, check=True)
            for line in result.stdout.splitlines():
                if 'worker' in line:
                    session_name = line.split(':')[0]
                    kill_session(session_name)
            logger.info("Stopped all existing tmux sessions")
        except subprocess.CalledProcessError as e:
            logger.warning(f"Error listing tmux sessions: {e.stderr.strip()}")
        start_index = 1
    else:
        logger.info("Add mode: Starting from the next available worker number")
        start_index = len([s for s in os.listdir('../') if s.startswith('worker') and s.endswith('.log')]) + 1

    for i in range(start_index, start_index + sessions):
        log_file = f'../worker{i}.log'
        session_name = f'worker{i}'
        try:
            start_session(session_name, worker_command, log_file)
            logger.info(f"Started tmux session {session_name} and logging to {log_file}")
            # Start a health check thread for each session
            threading.Thread(target=health_check, args=(session_name, log_file, worker_command), daemon=True).start()
        except Exception as e:
            logger.error(f"Failed to start tmux session {session_name} after multiple retries: {str(e)}")
            logger.error(f"Error traceback: {traceback.format_exc()}")
            # Log the contents of the worker log file for debugging
            try:
                with open(log_file, 'r') as f:
                    logger.error(f"Contents of {log_file}:\n{f.read()}")
            except Exception as read_error:
                logger.error(f"Failed to read {log_file}: {str(read_error)}")

    logger.info("Finished managing sessions")