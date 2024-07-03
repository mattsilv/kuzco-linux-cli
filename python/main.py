# File: main.py

import argparse
import logging
import threading
import time
import os
from logger import main_logger, config_logger, tmux_logger, monitor_logger
from config_loader import load_config
from tmux_manager import manage_sessions
from log_monitor import monitor_logs
from state_manager import clear_all_states

def clear_log_files(sessions):
    for i in range(1, sessions + 1):
        log_file = f'../worker{i}.log'
        if os.path.exists(log_file):
            with open(log_file, 'w') as f:
                f.write('')  # Clear the file
            print(f"Cleared {log_file}")

def main():
    parser = argparse.ArgumentParser(description='Kuzco Tmux Worker Manager')
    parser.add_argument('-m', '--mode', type=str, default='fresh', choices=['fresh', 'add'], help='Mode of operation')
    parser.add_argument('-s', '--sessions', type=int, default=5, help='Number of tmux sessions to start')
    parser.add_argument('-w', '--wait_time', type=int, default=5, help='Wait time between starting sessions')
    parser.add_argument('-r', '--retry_count', type=int, default=3, help='Number of retries for starting a session')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging')
    parser.add_argument('--auto-restart', action='store_true', help='Enable auto-restart for stuck workers')

    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    for logger in [main_logger, config_logger, tmux_logger, monitor_logger]:
        logger.setLevel(log_level)

    try:
        main_logger.info("Loading configuration...")
        config = load_config('../config.env')
        
        main_logger.info("Clearing log files and states...")
        clear_log_files(args.sessions)
        clear_all_states(args.sessions)

        main_logger.info("Starting tmux sessions...")
        tmux_thread = threading.Thread(target=manage_sessions, args=(config, args.mode, args.sessions, args.wait_time, args.retry_count))
        tmux_thread.start()

        # Start the log monitor immediately
        main_logger.info("Starting log monitor...")
        monitor_logs(args.sessions, config, True, args.auto_restart)
    except Exception as e:
        main_logger.error(f"An error occurred: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()