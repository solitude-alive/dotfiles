#!/bin/bash

cd "$(dirname "$0")" || exit 1

echo "Starting Dotfiles Setup..."
echo "=============================="

# --- module 1: Zsh set up ---
echo ">> [1/N] Setting up Zsh environment..."

./zsh/install.sh || {
  echo "Zsh setup failed!" >&2
  exit 1
}

echo "Zsh setup successfully."

echo "=============================="
# ：
# echo ">> [2/N] Setting up Git..."
# ./git/install.sh
# ...

echo "All setups completed successfully!"
