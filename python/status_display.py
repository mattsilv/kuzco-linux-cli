# File: status_display.py

import os
import time
from constants import WorkerStatus, ERROR_DISPLAY_TIME

def display_status(workers, elapsed_time):
    print("\033[H\033[J", end="")  # Clear screen
    print(f"Log Monitor - Elapsed Time: {int(elapsed_time)} seconds")
    print("-" * 50)
    for log_file, worker in workers.items():
        current_time = time.time()
        if worker.status == WorkerStatus.PRODUCTIVE:
            productive_time = int(current_time - worker.last_productive)
            status_line = f"{os.path.basename(log_file)}: {worker.status.value} as of {productive_time} seconds ago"
        elif worker.status == WorkerStatus.STARTING:
            status_line = f"{os.path.basename(log_file)}: {worker.status.value}"
        else:
            time_in_status = int(worker.get_time_in_status(current_time))
            status_line = f"{os.path.basename(log_file)}: {worker.status.value} for {time_in_status} seconds"
        
        if worker.restart_count > 0:
            status_line += f" (restart #{worker.restart_count})"
        
        if worker.error and current_time - worker.error_time <= ERROR_DISPLAY_TIME:
            status_line += f" - Error: {worker.error}"
        
        print(status_line)