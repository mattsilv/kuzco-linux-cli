import os
import time
from collections import defaultdict

def monitor_logs(sessions, log_file='../worker.log', max_init_time=30, productive_interval=30):
    logs = {f'worker{i}': {'last_heartbeat': 0, 'last_inference': 0, 'status': 'initializing', 'time_in_status': 0} for i in range(1, sessions + 1)}

    start_time = time.time()

    while True:
        current_time = time.time()
        elapsed_time = current_time - start_time

        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    for worker, data in logs.items():
                        if worker in line:
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

        for worker, data in logs.items():
            if data['status'] == 'alive' and current_time - data['last_inference'] > productive_interval:
                if data['status'] != 'unproductive':
                    data['status'] = 'unproductive'
                    data['time_in_status'] = elapsed_time

        os.system('clear')
        for worker, data in logs.items():
            time_in_status = int(elapsed_time - data['time_in_status'])
            print(f"{worker}: {data['status']} for {time_in_status} seconds")

        time.sleep(1)
