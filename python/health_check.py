# File: health_check.py

import time
import subprocess
from logger import tmux_logger as logger

def health_check(session_name, log_file, worker_command, check_interval=60):
    while True:
        time.sleep(check_interval)
        if not session_exists(session_name):
            logger.warning(f"Session {session_name} not found. Attempting to restart.")
            try:
                start_session(session_name, worker_command, log_file)
                logger.info(f"Restarted session {session_name}")
            except Exception as e:
                logger.error(f"Failed to restart session {session_name}: {str(e)}")
        else:
            # Check if the worker is responsive
            try:
                # This is a basic check. You may want to implement a more sophisticated check
                # based on the specific behavior of your Kuzco worker
                with open(log_file, 'r') as f:
                    last_lines = f.readlines()[-10:]  # Read last 10 lines
                    if any('Heartbeat' in line for line in last_lines):
                        logger.debug(f"Health check passed for session {session_name}")
                    else:
                        logger.warning(f"No recent heartbeat for session {session_name}. Restarting.")
                        kill_session(session_name)
                        start_session(session_name, worker_command, log_file)
            except Exception as e:
                logger.warning(f"Health check failed for session {session_name}: {str(e)}")

def session_exists(session_name):
    result = subprocess.run(['tmux', 'has-session', '-t', session_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.returncode == 0

def kill_session(session_name):
    try:
        subprocess.run(['tmux', 'kill-session', '-t', session_name], check=True, capture_output=True)
        logger.debug(f"Killed session '{session_name}'")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to kill session '{session_name}': {e.stderr.decode().strip()}")

def start_session(session_name, command, log_file):
    full_command = f'bash -c "{{ {command}; }} > {log_file} 2>&1 || {{ echo \\"Error occurred:\\" >&2; cat {log_file} >&2; }}"'
    try:
        subprocess.run(['tmux', 'new-session', '-d', '-s', session_name, full_command], check=True, capture_output=True)
        logger.debug(f"Started session '{session_name}'")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start session '{session_name}': {e.stderr.decode().strip()}")
        raise