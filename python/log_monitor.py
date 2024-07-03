# File: log_monitor.py

import os
import time
import logging
from collections import defaultdict
from tmux_manager import kill_session, start_session

def monitor_logs(sessions, max_init_time=30, productive_interval=30):
    logging.info(f"Starting log monitor for {sessions} sessions")
    logs = {f'../worker{i}.log': {
        'last_heartbeat': 0,
        'last_inference': 0,
        'last_init': 0,
        'status': 'initializing',
        'time_in_status': 0
    } for i in range(1, sessions + 1)}

    start_time = time.time()

    try:
        while True:
            current_time = time.time()
            elapsed_time = current_time - start_time

            for log_file, data in logs.items():
                if os.path.exists(log_file):
                    try:
                        with open(log_file, 'r') as f:
                            lines = f.readlines()
                            for line in lines:
                                if 'Heartbeat' in line:
                                    data['last_heartbeat'] = current_time
                                elif 'Inference finished' in line:
                                    data['last_inference'] = current_time
                                    data['status'] = 'productive'
                                    data['time_in_status'] = elapsed_time
                                elif 'Inference started' in line:
                                    data['status'] = 'productive'
                                    data['time_in_status'] = elapsed_time
                                elif 'Instance is initializing' in line:
                                    if data['status'] != 'initializing':
                                        data['status'] = 'initializing'
                                        data['last_init'] = current_time
                                        data['time_in_status'] = elapsed_time

                        # Check if initialization is taking too long
                        if data['status'] == 'initializing' and current_time - data['last_init'] > max_init_time:
                            logging.warning(f"{log_file}: Initialization taking too long. Restarting session.")
                            session_name = f"worker{log_file.split('worker')[1].split('.')[0]}"
                            kill_session(session_name)
                            start_session(session_name, 'kuzco worker start --worker {WORKER_ID} --code {CODE}', log_file)
                            data['last_init'] = current_time
                            data['time_in_status'] = elapsed_time

                        # Update status based on last inference time
                        if data['status'] == 'productive' and current_time - data['last_inference'] > productive_interval:
                            data['status'] = 'alive'
                            data['time_in_status'] = elapsed_time

                    except IOError as e:
                        logging.error(f"Error reading log file {log_file}: {str(e)}")
                else:
                    logging.warning(f"Log file not found: {log_file}")

            os.system('clear')
            print(f"Log Monitor - Elapsed Time: {int(elapsed_time)} seconds")
            print("-" * 50)
            for log_file, data in logs.items():
                time_in_status = int(elapsed_time - data['time_in_status'])
                print(f"{os.path.basename(log_file)}: {data['status']} for {time_in_status} seconds")
            
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Log monitor stopped by user")
    except Exception as e:
        logging.error(f"An error occurred in the log monitor: {str(e)}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    monitor_logs(5)  # Monitor 5 sessions by default