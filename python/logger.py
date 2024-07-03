import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger(name, log_file, level=logging.INFO, max_size=5*1024*1024, backup_count=5):
    """Function to setup as many loggers as you want"""

    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs')
    os.makedirs(log_dir, exist_ok=True)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    handler = RotatingFileHandler(os.path.join(log_dir, log_file), maxBytes=max_size, backupCount=backup_count)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    # Also log to console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

# Create loggers for different components
main_logger = setup_logger('main', 'main.log')
config_logger = setup_logger('config', 'config.log')
tmux_logger = setup_logger('tmux', 'tmux.log')
monitor_logger = setup_logger('monitor', 'monitor.log')