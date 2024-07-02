#!/bin/bash
# Activate the virtual environment
source ./myenv/bin/activate

# Set the PYTHONPATH to include the python directory
export PYTHONPATH=$(pwd)/python

# Navigate to the python directory
cd python

# Run the main script
python main.py
