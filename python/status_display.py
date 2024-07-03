# File: status_display.py

import os

def display_status(workers, elapsed_time):
    print("\033[H\033[J", end="")  # Clear screen
    print(f"Log Monitor - Elapsed Time: {int(elapsed_time)} seconds")
    print("-" * 50)
    for log_file, worker in workers.items():
        if worker.status == 'productive':
            productive_time = int(time.time() - worker.last_productive)
            status_line = f"{os.path.basename(log_file)}: {worker.status} (as of {productive_time} seconds ago)"
        elif worker.status == 'initializing':
            init_time = int(time.time() - worker.last_init)
            status_line = f"{os.path.basename(log_file)}: {worker.status} for {init_time} seconds (restart #{worker.restart_count})"
        else:
            time_in_status = int(time.time() - worker.last_init)
            status_line = f"{os.path.basename(log_file)}: {worker.status} for {time_in_status} seconds"
        if worker.error:
            status_line += f" - Error: {worker.error}"
        print(status_line)