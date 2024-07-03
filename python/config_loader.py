import os
from logger import config_logger as logger

def load_config(config_file='../config.env'):
    config = {}
    logger.info(f"Attempting to load configuration from {config_file}")
    
    if os.path.exists(config_file):
        logger.debug(f"Config file found: {config_file}")
        try:
            with open(config_file) as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        config[key] = value
                        logger.debug(f"Loaded config: {key}={value}")
        except Exception as e:
            logger.error(f"Error reading config file: {str(e)}")
            raise
    else:
        logger.warning(f"Config file not found: {config_file}. Attempting to load from environment variables.")
        config['WORKER_ID'] = os.getenv('WORKER_ID')
        config['CODE'] = os.getenv('CODE')
        
        if config['WORKER_ID']:
            logger.debug("Loaded WORKER_ID from environment variable")
        if config['CODE']:
            logger.debug("Loaded CODE from environment variable")

    if not config.get('WORKER_ID') or not config.get('CODE'):
        error_msg = "Worker ID and Code must be set in config file or environment variables."
        logger.error(error_msg)
        raise ValueError(error_msg)

    logger.info("Configuration loaded successfully")
    return config