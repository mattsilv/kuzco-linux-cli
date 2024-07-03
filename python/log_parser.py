# File: log_parser.py

import time

def parse_log(worker, log_lines, current_time, productive_interval=30):
    for line in log_lines:
        if 'Heartbeat' in line:
            worker.last_heartbeat = current_time
            if not worker.first_heartbeat:
                worker.first_heartbeat = True
                worker.start_time = current_time
                worker.status = 'initializing'
        elif 'Inference finished' in line or 'Inference started' in line:
            worker.last_inference = current_time
            worker.last_productive = current_time
            worker.status = 'productive'
        elif 'Initializing' in line:
            if worker.status != 'initializing':
                worker.status = 'initializing'
                worker.last_init = current_time
        elif 'SyntaxError' in line or 'Failed to handle inference subscription' in line:
            worker.error = line.strip()
            worker.status = 'error'
            worker.critical_error = True
        elif 'Error:' in line or 'Failed to' in line:
            worker.error = line.strip()
            worker.status = 'error'

    # Update status based on last productive time
    if worker.status == 'productive' and current_time - worker.last_productive > productive_interval:
        worker.status = 'unproductive'

    worker.time_in_status = current_time - (worker.last_productive if worker.status == 'productive' else worker.last_init)