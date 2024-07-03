# File: tmux_manager.py

import subprocess
import time
import os
from logger import tmux_logger as logger

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

def start_session(session_name, worker_id, code, log_file):
    logger.info(f"Starting session '{session_name}'")
    command = f'kuzco worker start --worker {worker_id} --code {code}'
    full_command = f'{command} > {log_file} 2>&1'
    try:
        subprocess.run(['tmux', 'new-session', '-d', '-s', session_name, 'bash', '-c', full_command], check=True, capture_output=True)
        logger.debug(f"Successfully started session '{session_name}'")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start session '{session_name}': {e.stderr.decode().strip()}")
        raise

def manage_sessions(config, mode='fresh', sessions=5, wait_time=5, retry_count=3):
    worker_id = config.get('WORKER_ID')
    code = config.get('CODE')
    
    if not worker_id or not code:
        raise ValueError("WORKER_ID and CODE must be set in the configuration")

    logger.info(f"Managing sessions: mode={mode}, sessions={sessions}, wait_time={wait_time}, retry_count={retry_count}")

    if mode == 'fresh':
        logger.info("Fresh mode: Stopping all existing tmux sessions")
        try:
            result = subprocess.run(['tmux', 'list-sessions'], capture_output=True, text=True, check=True)
            for line in result.stdout.splitlines():
                session_name = line.split(':')[0]
                try:
                    kill_session(session_name)
                    logger.info(f"Stopped session: {session_name}")
                except Exception as e:
                    logger.error(f"Failed to stop session {session_name}: {str(e)}")
            logger.info("Attempted to stop all existing tmux sessions")
        except subprocess.CalledProcessError as e:
            if "no server running" in e.stderr.lower():
                logger.info("No tmux server running. No sessions to stop.")
            else:
                logger.warning(f"Error listing tmux sessions: {e.stderr.strip()}")
        start_index = 1
    else:
        logger.info("Add mode: Starting from the next available worker number")
        start_index = len([s for s in os.listdir('../') if s.startswith('worker') and s.endswith('.log')]) + 1

    for i in range(start_index, start_index + sessions):
        log_file = f'../worker{i}.log'
        session_name = f'worker{i}'
        success = False
        for attempt in range(1, retry_count + 1):
            logger.info(f"Attempting to start session {session_name} (attempt {attempt}/{retry_count})")
            if session_exists(session_name):
                kill_session(session_name)
            try:
                start_session(session_name, worker_id, code, log_file)
                time.sleep(wait_time)
                if session_exists(session_name):
                    success = True
                    logger.info(f"Successfully started session {session_name} on attempt {attempt}")
                    break
                else:
                    logger.warning(f"Session {session_name} not found after starting, retrying...")
            except Exception as e:
                logger.error(f"Error starting session {session_name} on attempt {attempt}: {str(e)}")

        if success:
            logger.info(f"Started tmux session {session_name} and logging to {log_file}")
        else:
            logger.error(f"Failed to start tmux session {session_name} after {retry_count} attempts")

    logger.info("Finished managing sessions")