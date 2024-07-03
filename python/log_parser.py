# File: log_parser.py

import time

def parse_log(worker, log_lines, current_time):
    for line in log_lines:
        if 'Heartbeat' in line:
            worker.last_heartbeat = current_time
            if not worker.first_heartbeat:
                worker.first_heartbeat = True
                worker.start_time = current_time
            if worker.status == 'initializing' and current_time - worker.start_time >= 20:
                worker.update_status('unproductive', current_time)
        elif 'Inference finished' in line or 'Inference started' in line:
            worker.last_inference = current_time
            worker.last_productive = current_time
            if worker.status != 'initializing':
                worker.update_status('productive', current_time)
        elif 'Initializing' in line:
            if worker.status != 'initializing':
                worker.update_status('initializing', current_time)
                worker.last_init = current_time
        elif 'SyntaxError' in line or 'Failed to handle inference subscription' in line:
            worker.error = line.strip()
            worker.update_status('error', current_time)
            worker.critical_error = True
        elif 'Error:' in line or 'Failed to' in line:
            worker.error = line.strip()
            worker.update_status('error', current_time)

    # Update status based on last inference time
    if worker.status == 'productive' and current_time - worker.last_productive > 30:  # 30 seconds threshold
        worker.update_status('unproductive', current_time)