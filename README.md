# Kuzco Python Worker Manager

This Python script manages Kuzco workers using tmux sessions. It provides functionality for starting, monitoring, and managing multiple worker instances through a command-line interface.

## Features

- Starts and manages multiple Kuzco workers in tmux sessions
- Supports two modes: fresh start and adding sessions
- Reads worker configuration from a local config file or environment variables
- Monitors worker health and automatically restarts unresponsive workers
- Provides real-time status updates for all worker instances

## Requirements

- Python 3.6+
- `tmux` must be installed on your system
- Required Python packages: `subprocess`, `argparse`, `logging`

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/mattsilv/kuzco-linux-cli.git
   cd kuzco-linux-cli/python
   ```

2. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Create a `config.env` file in the parent directory of the script. This file should contain your worker ID and code:

```bash
# config.env
WORKER_ID=your_worker_id
CODE=your_code
```

Alternatively, you can set the `WORKER_ID` and `CODE` as environment variables:

```bash
export WORKER_ID="your_worker_id"
export CODE="your_code"
```

## Usage

Run the script using Python with various command-line arguments:

```bash
python main.py [-h] [-m {fresh,add}] [-s SESSIONS] [-w WAIT_TIME] [-r RETRY_COUNT] [-v]
```

Arguments:

- `-m, --mode {fresh,add}`: Mode of operation (default: fresh)
- `-s, --sessions SESSIONS`: Number of tmux sessions to start (default: 5)
- `-w, --wait_time WAIT_TIME`: Wait time between starting sessions (default: 5)
- `-r, --retry_count RETRY_COUNT`: Number of retries for starting a session (default: 3)
- `-v, --verbose`: Enable verbose logging

Example usage:

```bash
# Start 10 fresh tmux sessions with verbose logging
python main.py -m fresh -s 10 -v

# Add 3 tmux sessions to existing ones
python main.py -m add -s 3
```

## Components

1. `main.py`: The entry point of the application. It parses command-line arguments and initializes the worker management process.
2. `config_loader.py`: Handles loading of configuration from the `config.env` file or environment variables.
3. `tmux_manager.py`: Manages tmux sessions, including starting, stopping, and checking the status of sessions.
4. `log_monitor.py`: Monitors worker logs, updates worker statuses, and handles automatic restarts of unresponsive workers.
5. `logger.py`: Sets up logging for different components of the application.

## Worker Statuses

The log monitor tracks the following statuses for each worker:

- `initializing`: The worker is starting up.
- `productive`: The worker has successfully run an inference in the last 30 seconds.
- `alive`: The worker is running but hasn't performed an inference in the last 30 seconds.
- `problem`: The worker is unresponsive or has encountered an issue.

## Troubleshooting

If workers are not starting or are frequently restarting, check the following:

1. Ensure your `WORKER_ID` and `CODE` are correct in the `config.env` file or environment variables.
2. Check the worker log files (located in the parent directory) for any error messages.
3. Verify that you have sufficient system resources to run the requested number of workers.
4. Ensure that the Kuzco CLI tool is properly installed and accessible in your system path.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).
