# File: worker_state.py

import time

class Worker:
    def __init__(self, log_file, show_loading=False):
        self.log_file = log_file
        self.last_heartbeat = 0
        self.last_inference = 0
        self.last_init = time.time()
        self.status = 'loading' if show_loading else 'initializing'
        self.time_in_status = 0
        self.error = None
        self.start_time = None
        self.critical_error = False
        self.first_heartbeat = False
        self.last_productive = 0
        self.restart_count = 0

    def restart(self):
        self.last_init = time.time()
        self.time_in_status = 0
        self.status = 'initializing'
        self.error = None
        self.critical_error = False
        self.last_inference = 0
        self.first_heartbeat = False
        self.start_time = None
        self.last_productive = 0
        self.restart_count += 1

    def update_status(self, new_status, current_time):
        self.status = new_status
        self.time_in_status = current_time - self.last_init