import os
import time

def monitor_logs(sessions, max_init_time=30, productive_interval=30):
    logs = {f'../worker{i}.log': {'last_heartbeat': 0, 'last_inference': 0, 'status': 'initializing'} for i in range(1, sessions + 1)}

    while True:
        current_time = time.time()
        for log_file, data in logs.items():
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    for line in lines:
                        if 'Heartbeat' in line:
                            data['last_heartbeat'] = current_time
                            data['status'] = 'alive'
                        elif 'Inference finished' in line:
                            data['last_inference'] = current_time
                            data['status'] = 'productive'
                        elif 'Initializing' in line:
                            if current_time - data['last_heartbeat'] > max_init_time:
                                data['status'] = 'problem'
        
        for log_file, data in logs.items():
            if data['status'] == 'alive' and current_time - data['last_inference'] > productive_interval:
                data['status'] = 'unproductive'
        
        for log_file, data in logs.items():
            print(f"{log_file}: {data['status']}")

        time.sleep(5)
