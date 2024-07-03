# File: log_monitor.py

import os
import time
import logging
from collections import defaultdict
from tmux_manager import kill_session, start_session

def monitor_logs(sessions, config, show_loading=False, auto_restart=False, max_init_time=90, productive_interval=30):
    logging.info(f"Starting log monitor for {sessions} sessions")
    logs = {f'../worker{i}.log': {
        'last_heartbeat': 0,
        'last_inference': 0,
        'last_init': time.time(),
        'status': 'loading' if show_loading else 'initializing',
        'time_in_status': 0,
        'error': None,
        'start_time': None,
        'critical_error': False,
        'first_heartbeat': False,
        'productive_since': 0
    } for i in range(1, sessions + 1)}

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
            logs[log_file]['last_init'] = time.time()
            logs[log_file]['time_in_status'] = 0
            logs[log_file]['status'] = 'initializing'
            logs[log_file]['error'] = None
            logs[log_file]['critical_error'] = False
            logs[log_file]['last_inference'] = 0
            logs[log_file]['first_heartbeat'] = False
            logs[log_file]['start_time'] = None
            logs[log_file]['productive_since'] = 0
        except Exception as e:
            logging.error(f"Failed to restart session {session_name}: {str(e)}")
            logs[log_file]['status'] = 'error'
            logs[log_file]['error'] = f"Restart failed: {str(e)}"

    try:
        while True:
            current_time = time.time()
            elapsed_time = current_time - start_time

            for log_file, data in logs.items():
                if os.path.exists(log_file):
                    if data['status'] == 'loading':
                        data['status'] = 'initializing'
                        data['time_in_status'] = elapsed_time
                        data['last_init'] = current_time
                    try:
                        with open(log_file, 'r') as f:
                            lines = f.readlines()
                            for line in lines:
                                if 'Heartbeat' in line:
                                    data['last_heartbeat'] = current_time
                                    if not data['first_heartbeat']:
                                        data['first_heartbeat'] = True
                                        data['start_time'] = current_time
                                    if data['status'] == 'initializing' and current_time - data['start_time'] >= 20:
                                        data['status'] = 'alive'
                                        data['time_in_status'] = elapsed_time
                                elif 'Inference finished' in line or 'Inference started' in line:
                                    data['last_inference'] = current_time
                                    if data['status'] != 'initializing':
                                        if data['status'] != 'productive':
                                            data['productive_since'] = current_time
                                        data['status'] = 'productive'
                                        data['time_in_status'] = elapsed_time
                                elif 'Initializing' in line:
                                    if data['status'] != 'initializing':
                                        data['status'] = 'initializing'
                                        data['last_init'] = current_time
                                        data['time_in_status'] = elapsed_time
                                elif 'SyntaxError' in line or 'Failed to handle inference subscription' in line:
                                    data['error'] = line.strip()
                                    data['status'] = 'error'
                                    data['time_in_status'] = elapsed_time
                                    data['critical_error'] = True
                                elif 'Error:' in line or 'Failed to' in line:
                                    data['error'] = line.strip()
                                    data['status'] = 'error'
                                    data['time_in_status'] = elapsed_time

                        if data['critical_error']:
                            restart_worker(log_file, "Critical error detected.")
                        elif auto_restart and data['status'] == 'initializing' and current_time - data['last_init'] > max_init_time:
                            restart_worker(log_file, "Initialization taking too long.")

                        # Update status based on last inference time
                        if data['status'] == 'productive' and current_time - data['last_inference'] > productive_interval:
                            data['status'] = 'alive'
                            data['time_in_status'] = elapsed_time
                            data['productive_since'] = 0
                        elif data['status'] == 'alive' and current_time - data['last_inference'] <= productive_interval and data['start_time'] and current_time - data['start_time'] >= 20:
                            data['status'] = 'productive'
                            data['time_in_status'] = elapsed_time
                            data['productive_since'] = current_time

                    except IOError as e:
                        logging.error(f"Error reading log file {log_file}: {str(e)}")
                else:
                    if data['status'] != 'loading':
                        logging.warning(f"Log file not found: {log_file}")
                    
                    if auto_restart and current_time - data['last_init'] > max_init_time:
                        restart_worker(log_file, "Worker stuck in loading state.")

            # Use ANSI escape codes to move cursor to top of screen and clear
            print("\033[H\033[J", end="")
            print(f"Log Monitor - Elapsed Time: {int(elapsed_time)} seconds")
            print("-" * 50)
            for log_file, data in logs.items():
                if data['status'] == 'productive':
                    productive_time = int(current_time - data['productive_since'])
                    status_line = f"{os.path.basename(log_file)}: {data['status']} for {productive_time} seconds"
                else:
                    time_in_status = int(elapsed_time - data['time_in_status'])
                    status_line = f"{os.path.basename(log_file)}: {data['status']} for {time_in_status} seconds"
                if data['error']:
                    status_line += f" - Error: {data['error']}"
                print(status_line)
            
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