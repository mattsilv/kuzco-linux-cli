# File: constants.py

from enum import Enum

class WorkerStatus(Enum):
    STARTING = 'starting'
    CONNECTING = 'connecting'  # New status
    INITIALIZING = 'initializing'
    PRODUCTIVE = 'productive'
    UNPRODUCTIVE = 'unproductive'
    ERROR = 'error'

MAX_INIT_TIME = 90
PRODUCTIVE_INTERVAL = 30
ERROR_DISPLAY_TIME = 5