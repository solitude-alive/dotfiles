#!/bin/bash

# Ensure the script runs from the directory where it resides
cd "$(dirname "$0")" || exit
CURRENT_DIR=$(pwd)

echo "Starting Python environment setup (Compatibility Mode)..."

# ==============================================================================
# Step 1: Smart uv Installation/Update
# ==============================================================================
if command -v uv &>/dev/null; then
  UV_PATH=$(command -v uv)
  echo "uv is already installed at: $UV_PATH"

  echo "   Checking for updates..."

  # Capture output to check for "managed by package manager" error
  # redirect stderr to stdout to capture error messages
  UPDATE_MSG=$(uv self update 2>&1)
  UPDATE_EXIT_CODE=$?

  if [ "$UPDATE_EXIT_CODE" -eq 0 ]; then
    echo "   > uv updated successfully."
  else
    # Check if failure is due to being managed by Homebrew or system
    if [[ "$UPDATE_MSG" == *"managed by"* ]] || [[ "$UV_PATH" == *"homebrew"* ]]; then
      echo "   > Skipped 'uv self update' (It seems managed by Homebrew or system)."
      echo "   > Recommendation: Run 'brew upgrade uv' manually if needed."
    else
      echo "   > Warning: uv update failed with message:"
      echo "     $UPDATE_MSG"
    fi
  fi
else
  echo "Installing uv (fast package manager)..."
  curl -LsSf https://astral.sh/uv/install.sh | sh

  # Temporarily add to PATH so we can use it immediately in this script
  export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
fi

if ! command -v uv &>/dev/null; then
  echo "Error: uv installation failed or is not in PATH."
  echo "Please restart your terminal or check ~/.local/bin or ~/.cargo/bin"
  exit 1
fi

# ==============================================================================
# Step 2: Smart Global Tool Management
# ==============================================================================
# Function to safely install or upgrade a tool
ensure_tool() {
  local tool_name=$1
  echo "  Checking tool: $tool_name..."

  # Check if tool is already installed via uv
  if uv tool list | grep -q "^$tool_name "; then
    echo "   > $tool_name is already installed. Upgrading..."
    uv tool upgrade "$tool_name"
  else
    echo "   > Installing $tool_name..."
    uv tool install "$tool_name"
  fi
}

# 1. Ruff (Linter & Formatter)
ensure_tool "ruff"

# 2. Pre-commit (Git Hooks manager)
ensure_tool "pre-commit"

# ==============================================================================
# Step 3: Global Configuration (Respecting Defaults)
# ==============================================================================
CONFIG_DIR="$HOME/.config/ruff"

echo "🔗 Linking global Ruff configuration..."
if [ ! -d "$CONFIG_DIR" ]; then
  mkdir -p "$CONFIG_DIR"
fi

# Logic: Only backup if it's a REAL file (user created), not if it's already a symlink.
TARGET_FILE="$CONFIG_DIR/ruff.toml"
SOURCE_FILE="$CURRENT_DIR/ruff.toml"

if [ -L "$TARGET_FILE" ]; then
  # It's already a symlink. Check if it points to the right place.
  LINK_DEST=$(readlink "$TARGET_FILE")
  if [ "$LINK_DEST" == "$SOURCE_FILE" ]; then
    echo "   > Link already correct."
  else
    echo "   > Updating symlink..."
    ln -sf "$SOURCE_FILE" "$TARGET_FILE"
  fi
elif [ -f "$TARGET_FILE" ]; then
  # It's a real file. Backup required!
  echo "️  Existing ruff.toml found (Not a symlink)."
  BACKUP_NAME="$TARGET_FILE.backup.$(date +%s)"
  echo "   > Backing up to $BACKUP_NAME"
  mv "$TARGET_FILE" "$BACKUP_NAME"

  echo "   > Creating new symlink..."
  ln -sf "$SOURCE_FILE" "$TARGET_FILE"
else
  # File doesn't exist. Just link it.
  ln -sf "$SOURCE_FILE" "$TARGET_FILE"
  echo "   > Link created."
fi

echo "Python setup complete!"
