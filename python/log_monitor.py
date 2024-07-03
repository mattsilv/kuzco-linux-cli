# File: log_monitor.py

import os
import time
import logging
from worker_state import Worker
from log_parser import parse_log
from status_display import display_status
from tmux_manager import kill_session, start_session

def monitor_logs(sessions, config, show_loading=False, auto_restart=False, max_init_time=90, productive_interval=30):
    logging.info(f"Starting log monitor for {sessions} sessions")
    workers = {f'../worker{i}.log': Worker(f'../worker{i}.log', show_loading) for i in range(1, sessions + 1)}

    worker_id = config.get('WORKER_ID')
    code = config.get('CODE')

    if not worker_id or not code:
        raise ValueError("WORKER_ID and CODE must be set in the configuration")

    start_time = time.time()

    def restart_worker(log_file, reason):
        session_name = f"worker{log_file.split('worker')[1].split('.')[0]}"
        logging.warning(f"{log_file}: {reason} Restarting session.")
        kill_session(session_name)
        try:
            start_session(session_name, worker_id, code, log_file)
            workers[log_file].restart()
        except Exception as e:
            logging.error(f"Failed to restart session {session_name}: {str(e)}")
            workers[log_file].status = 'error'
            workers[log_file].error = f"Restart failed: {str(e)}"

    try:
        while True:
            current_time = time.time()
            elapsed_time = current_time - start_time

            for log_file, worker in workers.items():
                if os.path.exists(log_file):
                    try:
                        with open(log_file, 'r') as f:
                            lines = f.readlines()
                        parse_log(worker, lines, current_time, productive_interval)

                        if worker.critical_error:
                            restart_worker(log_file, "Critical error detected.")
                        elif auto_restart and worker.status == 'initializing' and current_time - worker.last_init > max_init_time:
                            restart_worker(log_file, "Initialization taking too long.")

                    except IOError as e:
                        logging.error(f"Error reading log file {log_file}: {str(e)}")
                else:
                    if worker.status != 'loading':
                        logging.warning(f"Log file not found: {log_file}")
                    
                    if auto_restart and current_time - worker.last_init > max_init_time:
                        restart_worker(log_file, "Worker stuck in loading state.")

            display_status(workers, elapsed_time)
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Log monitor stopped by user")
    except Exception as e:
        logging.error(f"An error occurred in the log monitor: {str(e)}")
        logging.exception("Exception details:")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    # Note: You would need to pass the config when calling this function
    # monitor_logs(5, config, True, False)  # Monitor 5 sessions by default, show loading state, auto-restart disabled