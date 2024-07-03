# File: state_manager.py

import json
import os
from constants import WorkerStatus

STATE_DIR = '../worker_states'

def ensure_state_dir():
    os.makedirs(STATE_DIR, exist_ok=True)

def get_state_file(worker_id):
    return os.path.join(STATE_DIR, f'worker{worker_id}_state.json')

def save_worker_state(worker_id, state):
    ensure_state_dir()
    with open(get_state_file(worker_id), 'w') as f:
        json.dump({
            'status': state.status.value,
            'last_productive': state.last_productive,
            'error': state.error,
            'restart_count': state.restart_count
        }, f)

def load_worker_state(worker_id):
    state_file = get_state_file(worker_id)
    if os.path.exists(state_file):
        with open(state_file, 'r') as f:
            data = json.load(f)
        return data
    return None

def clear_all_states(sessions):
    ensure_state_dir()
    for i in range(1, sessions + 1):
        state_file = get_state_file(i)
        if os.path.exists(state_file):
            os.remove(state_file)