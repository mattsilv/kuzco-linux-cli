import os
import time
from collections import defaultdict

def monitor_logs(sessions, max_init_time=30, productive_interval=30):
    logs = {f'worker{i}.log': {'last_heartbeat': 0, 'last_inference': 0, 'status': 'initializing', 'time_in_status': 0} for i in range(1, sessions + 1)}

    start_time = time.time()

    while True:
        current_time = time.time()
        elapsed_time = current_time - start_time

        for log_file, data in logs.items():
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    for line in lines:
                        if 'Heartbeat' in line:
                            data['last_heartbeat'] = current_time
                            if data['status'] != 'alive':
                                data['status'] = 'alive'
                                data['time_in_status'] = elapsed_time
                        elif 'Inference finished' in line:
                            data['last_inference'] = current_time
                            if data['status'] != 'productive':
                                data['status'] = 'productive'
                                data['time_in_status'] = elapsed_time
                        elif 'Initializing' in line:
                            if current_time - data['last_heartbeat'] > max_init_time:
                                data['status'] = 'problem'
                                data['time_in_status'] = elapsed_time

            if data['status'] == 'alive' and current_time - data['last_inference'] > productive_interval:
                if data['status'] != 'unproductive':
                    data['status'] = 'unproductive'
                    data['time_in_status'] = elapsed_time

        os.system('clear')
        for log_file, data in logs.items():
            time_in_status = int(elapsed_time - data['time_in_status'])
            print(f"{log_file}: {data['status']} for {time_in_status} seconds")

        time.sleep(1)
