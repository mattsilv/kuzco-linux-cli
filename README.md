# Tmux Kuzco Worker Script

This script manages tmux sessions for running Kuzco workers. It allows for starting, stopping, and adding worker sessions easily through a command-line interface.

## Features

- Starts tmux sessions with specified commands
- Supports two modes: fresh start and adding sessions
- Reads worker configuration from a local config file or environment variables
- Allows specifying the number of tmux sessions to start via a command-line flag

## Requirements

- `tmux` must be installed on your system

## Usage

### 1. Set Up Configuration

Clone this repo

```bash
git clone https://github.com/mattsilv/kuzco-linux-cli.git .
```

Create a `config.env` file in the same directory as the script. This file should contain your worker ID and code. Here's an example:

```bash
cd kuzco-linux-cli
nano config.env
```

Paste in the contents below with your worker and code populated. hit CTRL-X, then ENTER to save the file in the nano editor.

```bash
# config.env
WORKER_ID=your_worker_id
CODE=your_code
```

Alternatively, you can set the `WORKER_ID` and `CODE` as environment variables.

```bash
# If env variables are defined, script will ignore the config.env file.
export WORKER_ID="your_worker_id"
export CODE="your_code"
```

### 2. Run the Script

The script can be executed with different flags to control its behavior:

- `-m [fresh|add]`: Mode of operation. Use `fresh` to kill all existing tmux sessions and start new ones. Use `add` to detect running tmux sessions and add new ones.
- `-s [number]`: Number of tmux sessions to start.

Example usage:

```bash

# Start 12 fresh tmux sessions
bash start.sh -m fresh -s 12

# Add 5 tmux sessions to the existing ones
bash start.sh -m add -s 5
```

## Script Details

Here's a brief overview of what the script does:

1. **Configuration Loading**: Checks for a `config.env` file. If found, it loads the worker ID and code from this file. If not found, it looks for these values in the environment variables.
2. **Command Definition**: Defines the command to start a Kuzco worker using the loaded configuration.
3. **Mode Handling**: Depending on the `-m` flag, the script will either kill all existing tmux sessions (`fresh` mode) or add to the existing sessions (`add` mode).
4. **Session Management**: Starts the specified number of tmux sessions using the defined command.

## License

This project is open source and available under the [MIT License](LICENSE).

## Contributions

Contributions are welcome! Please open an issue or submit a pull request on GitHub.
