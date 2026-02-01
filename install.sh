#!/bin/bash

cd "$(dirname "$0")" || exit 1

TOTAL_MODULES=3

echo "Starting Dotfiles Setup..."
echo "=============================="

# --- module 1: Zsh set up ---
echo ">> [1/$TOTAL_MODULES] Setting up Zsh environment..."

./zsh/install.sh || {
  echo "Zsh setup failed!" >&2
  exit 1
}

echo "Zsh setup successfully."
echo "=============================="

# --- module 2: Git set up ---
echo ">> [2/$TOTAL_MODULES] Setting up Git..."
./git/install.sh || {
  echo "Git setup failed!" >&2
  exit 1
}

echo "Git setup successfully."
echo "=============================="

# --- module 3: Python set up ---
echo ">> [3/$TOTAL_MODULES] Setting up Python environment..."
./python/install.sh || {
  echo "Python setup failed!" >&2
  exit 1
}

echo "Python setup successfully."
echo "=============================="

# --- next modules can be added here ---

echo "All setups completed successfully!"
