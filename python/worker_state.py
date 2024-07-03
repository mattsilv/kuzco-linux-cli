# File: worker_state.py

import time
from typing import Optional
from constants import WorkerStatus
from state_manager import save_worker_state, load_worker_state

class Worker:
    def __init__(self, log_file: str):
        self.log_file: str = log_file
        self.worker_id = int(log_file.split('worker')[1].split('.')[0])
        self.load_state()

    def load_state(self):
        state = load_worker_state(self.worker_id)
        if state:
            self.status = WorkerStatus(state['status'])
            self.last_productive = state['last_productive']
            self.error = state['error']
            self.restart_count = state['restart_count']
        else:
            self.reset()

    def save_state(self):
        save_worker_state(self.worker_id, self)

    def reset(self) -> None:
        current_time = time.time()
        self.last_heartbeat: float = current_time
        self.last_inference: float = current_time
        self.last_init: float = current_time
        self.status: WorkerStatus = WorkerStatus.STARTING
        self.time_in_status: float = 0
        self.error: Optional[str] = None
        self.error_time: float = 0
        self.start_time: float = current_time
        self.critical_error: bool = False
        self.first_heartbeat: bool = False
        self.last_productive: float = current_time
        self.last_status_change: float = current_time
        self.restart_count: int = 0
        self.save_state()

    def restart(self) -> None:
        self.reset()
        self.restart_count += 1
        self.save_state()

    def update_status(self, new_status: WorkerStatus, current_time: float) -> None:
        if self.status != new_status:
            self.last_status_change = current_time
        self.status = new_status
        if new_status == WorkerStatus.PRODUCTIVE:
            self.last_productive = current_time
        elif new_status == WorkerStatus.INITIALIZING:
            self.last_init = current_time
        if new_status != WorkerStatus.ERROR:
            self.error = None
            self.error_time = 0
        self.save_state()

    def set_error(self, error_message: str, current_time: float) -> None:
        self.error = error_message
        self.error_time = current_time
        self.update_status(WorkerStatus.ERROR, current_time)

    def get_time_in_status(self, current_time: float) -> float:
        return current_time - self.last_status_change