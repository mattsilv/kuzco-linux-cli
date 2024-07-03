# File: main.py

import argparse
from logger import main_logger as logger
from config_loader import load_config
from tmux_manager import manage_sessions
from log_monitor import monitor_logs

def main():
    parser = argparse.ArgumentParser(description='Kuzco Tmux Worker Manager')
    parser.add_argument('-m', '--mode', type=str, default='fresh', choices=['fresh', 'add'], help='Mode of operation')
    parser.add_argument('-s', '--sessions', type=int, default=5, help='Number of tmux sessions to start')
    parser.add_argument('-w', '--wait_time', type=int, default=5, help='Wait time between starting sessions')
    parser.add_argument('-r', '--retry_count', type=int, default=3, help='Number of retries for starting a session')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging')

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logger.DEBUG)

    try:
        logger.info(f"Starting Kuzco Tmux Worker Manager in {args.mode} mode")
        config = load_config('../config.env')
        logger.debug(f"Loaded configuration: {config}")

        manage_sessions(config, args.mode, args.sessions, args.wait_time, args.retry_count)
        monitor_logs(args.sessions)
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()