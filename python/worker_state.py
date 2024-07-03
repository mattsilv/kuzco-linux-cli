# File: worker_state.py

import time

class Worker:
    def __init__(self, log_file, show_loading=False):
        self.log_file = log_file
        self.last_heartbeat = 0
        self.last_inference = 0
        self.last_init = time.time()
        self.status = 'starting'
        self.time_in_status = 0
        self.error = None
        self.error_time = 0
        self.start_time = None
        self.critical_error = False
        self.first_heartbeat = False
        self.last_productive = 0
        self.restart_count = 0

    def restart(self):
        self.last_init = time.time()
        self.time_in_status = 0
        self.status = 'starting'
        self.error = None
        self.error_time = 0
        self.critical_error = False
        self.last_inference = 0
        self.first_heartbeat = False
        self.start_time = None
        self.last_productive = 0
        self.restart_count += 1

    def update_status(self, new_status, current_time):
        self.status = new_status
        self.time_in_status = current_time - self.last_init
        if new_status != 'error':
            self.error = None
            self.error_time = 0

    def set_error(self, error_message, current_time):
        self.error = error_message
        self.error_time = current_time
        self.status = 'error'
        self.time_in_status = 0