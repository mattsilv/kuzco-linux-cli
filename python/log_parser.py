# File: log_parser.py

import time

def parse_log(worker, log_lines, current_time, productive_interval=30):
    latest_error_time = 0
    latest_error = None

    for line in log_lines:
        if 'Heartbeat' in line:
            worker.last_heartbeat = current_time
            if not worker.first_heartbeat:
                worker.first_heartbeat = True
                worker.start_time = current_time
                worker.update_status('initializing', current_time)
        elif 'Inference finished' in line or 'Inference started' in line:
            worker.last_inference = current_time
            worker.last_productive = current_time
            worker.update_status('productive', current_time)
        elif 'Initializing' in line:
            if worker.status != 'initializing':
                worker.update_status('initializing', current_time)
                worker.last_init = current_time
        elif 'SyntaxError' in line or 'Failed to handle inference subscription' in line:
            timestamp = extract_timestamp(line)
            if timestamp > latest_error_time:
                latest_error_time = timestamp
                latest_error = line.strip()
                worker.critical_error = True
        elif 'Error:' in line or 'Failed to' in line:
            timestamp = extract_timestamp(line)
            if timestamp > latest_error_time:
                latest_error_time = timestamp
                latest_error = line.strip()

    # Update status based on last productive time
    if worker.status == 'productive' and current_time - worker.last_productive > productive_interval:
        worker.update_status('unproductive', current_time)

    # Set the latest error if it's recent (within the last 5 seconds)
    if latest_error and current_time - latest_error_time <= 5:
        worker.set_error(latest_error, latest_error_time)

    worker.time_in_status = current_time - (worker.last_productive if worker.status == 'productive' else worker.last_init)

def extract_timestamp(line):
    # Implement a function to extract the timestamp from the log line
    # This is a placeholder implementation, adjust according to your log format
    try:
        timestamp_str = line.split()[0]
        return time.mktime(time.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S.%fZ"))
    except:
        return 0