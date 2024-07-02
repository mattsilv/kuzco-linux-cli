import os

def load_config(config_file='../config.env'):
    config = {}
    if os.path.exists(config_file):
        with open(config_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    config[key] = value
    else:
        config['WORKER_ID'] = os.getenv('WORKER_ID')
        config['CODE'] = os.getenv('CODE')

    if not config.get('WORKER_ID') or not config.get('CODE'):
        raise ValueError("Worker ID and Code must be set in config file or environment variables.")

    return config
