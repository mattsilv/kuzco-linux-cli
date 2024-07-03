# File: log_monitor.py

import os
import time
import threading
from worker_state import Worker
from log_parser import parse_log
from status_display import display_status
from tmux_manager import kill_session, start_session
from logger import monitor_logger as logger
from constants import WorkerStatus, MAX_INIT_TIME, PRODUCTIVE_INTERVAL

def monitor_logs(sessions, config, show_loading=False, auto_restart=False, max_init_time=MAX_INIT_TIME, productive_interval=PRODUCTIVE_INTERVAL):
    logger.info(f"Starting log monitor for {sessions} sessions")
    workers = {f'../worker{i}.log': Worker(f'../worker{i}.log') for i in range(1, sessions + 1)}

    worker_id = config.get('WORKER_ID')
    code = config.get('CODE')

    if not worker_id or not code:
        raise ValueError("WORKER_ID and CODE must be set in the configuration")

    start_time = time.time()

    # Reset all workers to starting state
    current_time = time.time()
    for worker in workers.values():
        worker.reset()
        worker.update_status(WorkerStatus.STARTING, current_time)

    def restart_worker(log_file, reason):
        session_name = f"worker{log_file.split('worker')[1].split('.')[0]}"
        logger.warning(f"{log_file}: {reason} Restarting session.")
        kill_session(session_name)
        try:
            start_session(session_name, worker_id, code, log_file)
            workers[log_file].restart()
            logger.info(f"Successfully restarted worker {session_name}")
        except Exception as e:
            logger.error(f"Failed to restart session {session_name}: {str(e)}", exc_info=True)
            workers[log_file].status = WorkerStatus.ERROR
            workers[log_file].error = f"Restart failed: {str(e)}"
        
        # Check if the worker started successfully
        time.sleep(5)  # Wait a bit for the worker to start
        if not os.path.exists(log_file) or os.path.getsize(log_file) == 0:
            logger.error(f"Worker {session_name} failed to create or write to its log file after restart")

    def monitor_thread():
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
                        elif auto_restart and worker.status == WorkerStatus.INITIALIZING and current_time - worker.last_init > max_init_time:
                            restart_worker(log_file, "Initialization taking too long.")

                    except IOError as e:
                        logger.error(f"Error reading log file {log_file}: {str(e)}")
                else:
                    if worker.status != WorkerStatus.STARTING:
                        logger.warning(f"Log file not found: {log_file}")
                    
                    if auto_restart and worker.status == WorkerStatus.STARTING and current_time - worker.last_init > max_init_time:
                        restart_worker(log_file, "Worker stuck in starting state.")

            time.sleep(1)

    # Start the monitoring thread
    threading.Thread(target=monitor_thread, daemon=True).start()

    # Display status in the main thread
    try:
        while True:
            current_time = time.time()
            elapsed_time = current_time - start_time
            display_status(workers, elapsed_time)
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Log monitor stopped by user")
    except Exception as e:
        logger.error(f"An error occurred in the log monitor: {str(e)}")
        logger.exception("Exception details:")

if __name__ == "__main__":
    # This part is not needed anymore as we're using the logger from logger.py
    pass