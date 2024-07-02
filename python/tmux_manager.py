import subprocess
import time
import os

def session_exists(session_name):
    result = subprocess.run(['tmux', 'has-session', '-t', session_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.returncode == 0

def kill_session(session_name):
    subprocess.run(['tmux', 'kill-session', '-t', session_name])

def start_session(session_name, command, log_file):
    full_command = f'{command} > >(tee -a {log_file}) 2> >(tee -a {log_file} >&2)'
    subprocess.run(['tmux', 'new-session', '-d', '-s', session_name, 'bash', '-c', full_command])

def manage_sessions(config, mode='fresh', sessions=5, wait_time=5, retry_count=3, log_file='../worker.log'):
    worker_command = f'kuzco worker start --worker {config["WORKER_ID"]} --code {config["CODE"]}'

    if mode == 'fresh':
        result = subprocess.run(['tmux', 'list-sessions'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.stdout:
            for line in result.stdout.decode().splitlines():
                if 'worker' in line:
                    session_name = line.split(':')[0]
                    kill_session(session_name)
        print("Stopped all existing tmux sessions.")
        start_index = 1
    else:
        start_index = len([s for s in os.listdir('../') if s.startswith('worker') and s.endswith('.log')]) + 1

    for i in range(start_index, start_index + sessions):
        success = False
        for _ in range(retry_count):
            if session_exists(f'worker{i}'):
                kill_session(f'worker{i}')
            start_session(f'worker{i}', worker_command, log_file)
            time.sleep(wait_time)
            success = True
            break

        if success:
            print(f"Started tmux session worker{i} and logging to {log_file}")
        else:
            print(f"Failed to start tmux session worker{i} after {retry_count} attempts")
