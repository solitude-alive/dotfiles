#!/bin/bash

# Ensure the script runs from the directory where it resides
cd "$(dirname "$0")" || exit
CURRENT_DIR=$(pwd)

# Define Paths
REPO_CONFIG_FILE="$CURRENT_DIR/gitconfig"  # The generic file in your repo
SYSTEM_CONFIG_FILE="$HOME/.gitconfig"      # The actual git config used by the system
LOCAL_CONFIG_FILE="$HOME/.gitconfig.local" # The private file for user identity

echo "Starting Git configuration setup (Include Mode)..."

# --- Step 1: Ensure ~/.gitconfig exists ---
if [ ! -f "$SYSTEM_CONFIG_FILE" ]; then
  touch "$SYSTEM_CONFIG_FILE"
  echo "   > Created empty ~/.gitconfig"
fi

# --- Step 2: Inject [include] into ~/.gitconfig ---
# Logic: We want to add the include path to the TOP of the file.
# This ensures repo config acts as a "Base", and system overrides take precedence.

INCLUDE_LINE="path = $REPO_CONFIG_FILE"

# Check if the path is already included (avoid duplicates)
if grep -Fq "$REPO_CONFIG_FILE" "$SYSTEM_CONFIG_FILE"; then
  echo "   > Repo config is already included in ~/.gitconfig. Skipping injection."
else
  echo "Injecting repository config into ~/.gitconfig..."

  # Create a temporary file
  TEMP_FILE=$(mktemp)

  # 1. Write the include block first
  {
    echo "[include]"
    echo "    $INCLUDE_LINE"
    echo
  } >"$TEMP_FILE"

  # 2. Append the original content of ~/.gitconfig
  cat "$SYSTEM_CONFIG_FILE" >>"$TEMP_FILE"

  # 3. Overwrite ~/.gitconfig with the new content
  mv "$TEMP_FILE" "$SYSTEM_CONFIG_FILE"
  echo "   > Successfully added [include] block."
fi

# --- Step 3: Configure Local Identity (~/.gitconfig.local) ---
echo "Checking Git Identity..."

# Create local file if it doesn't exist (to prevent errors when writing to it)
if [ ! -f "$LOCAL_CONFIG_FILE" ]; then
  echo "[user]" >"$LOCAL_CONFIG_FILE"
fi

# Check effective git configuration (Global scope)
CURRENT_NAME=$(git config --global user.name)
CURRENT_EMAIL=$(git config --global user.email)

# 3.1 Setup Name
if [ -z "$CURRENT_NAME" ]; then
  read -r -p "   > No identity found. Enter your Git Name (e.g., John Doe): " INPUT_NAME
  # Write specifically to the local file
  git config -f "$LOCAL_CONFIG_FILE" user.name "$INPUT_NAME"
  echo "   > Name saved to .gitconfig.local"
else
  echo "   > Name is set: $CURRENT_NAME"
fi

# 3.2 Setup Email
if [ -z "$CURRENT_EMAIL" ]; then
  read -r -p "   > No identity found. Enter your Git Email: " INPUT_EMAIL
  # Write specifically to the local file
  git config -f "$LOCAL_CONFIG_FILE" user.email "$INPUT_EMAIL"
  echo "   > Email saved to .gitconfig.local"
else
  echo "   > Email is set: $CURRENT_EMAIL"
fi

echo "Git setup complete!"
