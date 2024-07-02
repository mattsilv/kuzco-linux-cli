#!/bin/bash

# Ensure the .git/hooks directory exists
HOOKS_DIR=".git/hooks"
if [ ! -d "$HOOKS_DIR" ]; then
  echo "Error: .git/hooks directory does not exist. Are you sure this is a Git repository?"
  exit 1
fi

# Copy the post-merge hook to the .git/hooks directory
cp hooks/post-merge $HOOKS_DIR/post-merge

# Make the post-merge hook executable
chmod +x $HOOKS_DIR/post-merge

echo "Git hooks have been set up."