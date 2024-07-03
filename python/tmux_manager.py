# File: tmux_manager.py

import subprocess
import time
import os
import logging
from logger import tmux_logger as logger

# Set the logger to a higher level to suppress most logs
logger.setLevel(logging.WARNING)

def session_exists(session_name):
    result = subprocess.run(['tmux', 'has-session', '-t', session_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.returncode == 0

def kill_session(session_name):
    try:
        subprocess.run(['tmux', 'kill-session', '-t', session_name], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        logger.warning(f"Failed to kill session '{session_name}'")

def start_session(session_name, worker_id, code, log_file):
    command = f'kuzco worker start --worker {worker_id} --code {code}'
    full_command = f'{command} > {log_file} 2>&1'
    try:
        subprocess.run(['tmux', 'new-session', '-d', '-s', session_name, 'bash', '-c', full_command], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        logger.warning(f"Failed to start session '{session_name}'")
        raise

def manage_sessions(config, mode='fresh', sessions=5, wait_time=5, retry_count=3):
    worker_id = config.get('WORKER_ID')
    code = config.get('CODE')
    
    if not worker_id or not code:
        raise ValueError("WORKER_ID and CODE must be set in the configuration")

    if mode == 'fresh':
        try:
            result = subprocess.run(['tmux', 'list-sessions'], capture_output=True, text=True, check=True)
            for line in result.stdout.splitlines():
                session_name = line.split(':')[0]
                kill_session(session_name)
        except subprocess.CalledProcessError:
            pass  # Ignore errors when no tmux server is running

    start_index = 1 if mode == 'fresh' else len([s for s in os.listdir('../') if s.startswith('worker') and s.endswith('.log')]) + 1

    for i in range(start_index, start_index + sessions):
        log_file = f'../worker{i}.log'
        session_name = f'worker{i}'
        for attempt in range(1, retry_count + 1):
            if session_exists(session_name):
                kill_session(session_name)
            try:
                start_session(session_name, worker_id, code, log_file)
                time.sleep(wait_time)
                if session_exists(session_name):
                    break
            except Exception:
                if attempt == retry_count:
                    logger.error(f"Failed to start tmux session {session_name} after {retry_count} attempts")

    logger.info("Finished managing sessions")