# File: log_parser.py

import time
from constants import WorkerStatus, PRODUCTIVE_INTERVAL, ERROR_DISPLAY_TIME

def parse_log(worker, log_lines, current_time, productive_interval=PRODUCTIVE_INTERVAL):
    latest_error_time = 0
    latest_error = None
    was_productive = False

    for line in log_lines:
        if 'Heartbeat' in line:
            worker.last_heartbeat = current_time
            if not worker.first_heartbeat:
                worker.first_heartbeat = True
                worker.start_time = current_time
                worker.update_status(WorkerStatus.INITIALIZING, current_time)
        elif 'Inference finished' in line or 'Inference started' in line:
            worker.last_inference = current_time
            worker.last_productive = current_time
            was_productive = True
        elif 'Initializing' in line:
            worker.update_status(WorkerStatus.INITIALIZING, current_time)
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

    # Update status based on productivity
    if was_productive:
        worker.update_status(WorkerStatus.PRODUCTIVE, current_time)
    elif worker.status == WorkerStatus.PRODUCTIVE and current_time - worker.last_productive > productive_interval:
        worker.update_status(WorkerStatus.UNPRODUCTIVE, current_time)

    # Set the latest error if it's recent
    if latest_error and current_time - latest_error_time <= ERROR_DISPLAY_TIME:
        worker.set_error(latest_error, latest_error_time)

def extract_timestamp(line):
    # Implement a function to extract the timestamp from the log line
    # This is a placeholder implementation, adjust according to your log format
    try:
        timestamp_str = line.split()[0]
        return time.mktime(time.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S.%fZ"))
    except:
        return 0