#!/bin/bash

# get current dir (i.e., dotfiles/zsh)
CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ZSH_CUSTOM="${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}"

echo "Starting Zsh environment setup..."

# --- 1. Ensure zsh is installed ---
# command -v is POSIX and works on minimal images where `which` is missing.
if ! command -v zsh &>/dev/null; then
  echo "zsh is not installed, installing..."
  if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "macos detected, installing zsh via brew..."
    brew install zsh || {
      echo "Failed to install zsh via brew" >&2
      exit 1
    }
  elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "linux detected, installing zsh via apt..."
    if ! { sudo apt-get update && sudo apt-get install -y zsh; }; then
      echo "Failed to install zsh via apt" >&2
      exit 1
    fi
  else
    echo "unsupported os detected: $OSTYPE" >&2
    exit 1
  fi
else
  echo "zsh is already installed"
fi

# --- 2. Ensure zsh is the default login shell ---
# Runs for both "just installed" and "was already installed" paths, so a
# fresh-machine setup actually switches the default shell (previously this
# step was nested in the 'already installed' branch and skipped on first run).
ZSH_PATH="$(command -v zsh)"
# SUDO_USER is set by sudo to the invoking user's name; fall back to $USER.
# This makes the target correct whether the script is run as the user
# directly, or via `sudo ./install.sh` (where $USER would be "root").
TARGET_USER="${SUDO_USER:-$USER}"

if [[ "$SHELL" == "$ZSH_PATH" ]]; then
  echo "zsh is already the default shell"
else
  # On Linux, chsh rejects shells that are not listed in /etc/shells (common
  # when zsh was installed from a non-system path like Homebrew/linuxbrew).
  if [[ "$OSTYPE" == "linux-gnu"* ]] && ! grep -qxF "$ZSH_PATH" /etc/shells; then
    echo "Registering $ZSH_PATH in /etc/shells..."
    echo "$ZSH_PATH" | sudo tee -a /etc/shells >/dev/null
  fi

  echo "Setting zsh as the default shell for $TARGET_USER..."
  # Using `sudo chsh` (running as root) skips the user-password PAM prompt,
  # which would hang non-interactive environments (CI, containers, piped
  # bootstrap scripts). On passwordless-sudo hosts this is fully automatic.
  if ! sudo chsh -s "$ZSH_PATH" "$TARGET_USER"; then
    echo "Warning: could not change default shell automatically." >&2
    echo "         Retry manually: sudo chsh -s $ZSH_PATH $TARGET_USER" >&2
  fi
fi

# --- 3. Install Oh My Zsh ---
if [ ! -d "$HOME/.oh-my-zsh" ]; then
  echo "cloning Oh My Zsh..."
  # Use --unattended to avoid entering zsh immediately after installation, which can interrupt the script
  sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
else
  echo "Oh My Zsh is already installed"
fi

# --- 4. Download Powerlevel10k theme ---
if [ ! -d "$ZSH_CUSTOM/themes/powerlevel10k" ]; then
  echo "downloading Powerlevel10k theme..."
  git clone --depth=1 https://github.com/romkatv/powerlevel10k.git "$ZSH_CUSTOM/themes/powerlevel10k"
else
  echo "Powerlevel10k theme is already installed"
fi

# --- 5. Download plugins ---
echo "Installing/updating plugins..."
# Plugin: Auto Suggestions
if [ ! -d "$ZSH_CUSTOM/plugins/zsh-autosuggestions" ]; then
  git clone https://github.com/zsh-users/zsh-autosuggestions "$ZSH_CUSTOM/plugins/zsh-autosuggestions"
fi

# Plugin: Syntax Highlighting
if [ ! -d "$ZSH_CUSTOM/plugins/zsh-syntax-highlighting" ]; then
  git clone https://github.com/zsh-users/zsh-syntax-highlighting.git "$ZSH_CUSTOM/plugins/zsh-syntax-highlighting"
fi

# --- 6. Link platform-specific configuration files ---
echo "Linking configuration files..."

# pick source files by OS
if [[ "$OSTYPE" == "darwin"* ]]; then
  ALIASES_SRC="$CURRENT_DIR/.zsh_aliases.mac"
  P10K_SRC="$CURRENT_DIR/.p10k.mac.zsh"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
  ALIASES_SRC="$CURRENT_DIR/.zsh_aliases.linux"
  P10K_SRC="$CURRENT_DIR/.p10k.linux.zsh"
else
  echo "unsupported os for config linking: $OSTYPE" >&2
  exit 1
fi

# sanity check: source files must exist
for src in "$ALIASES_SRC" "$P10K_SRC"; do
  if [ ! -f "$src" ]; then
    echo "missing config file: $src" >&2
    exit 1
  fi
done

# backup .zsh_aliases
if [ -f "$HOME/.zsh_aliases" ] && [ ! -L "$HOME/.zsh_aliases" ]; then
  echo "Backing up existing .zsh_aliases to .zsh_aliases.backup.TIMESTAMP"
  mv "$HOME/.zsh_aliases" "$HOME/.zsh_aliases.backup.$(date +%s)"
fi
# backup .p10k.zsh
if [ -f "$HOME/.p10k.zsh" ] && [ ! -L "$HOME/.p10k.zsh" ]; then
  mv "$HOME/.p10k.zsh" "$HOME/.p10k.zsh.backup.$(date +%s)"
fi

## Create a symlink to use the platform-specific configuration from your repository
ln -sf "$ALIASES_SRC" "$HOME/.zsh_aliases"
ln -sf "$P10K_SRC" "$HOME/.p10k.zsh"

# --- 7. Create .zshrc entrypoint ---
ZSHRC_FILE="$HOME/.zshrc"
INIT_FILE="$CURRENT_DIR/init.zsh"

echo "Updating ~/.zshrc to source our init.zsh..."

# check .zshrc is already sourcing our init file
if grep -q "source $INIT_FILE" "$ZSHRC_FILE" 2>/dev/null; then
  echo " ~/.zshrc already sources your init file."
else
  # backup existing .zshrc if it's not a symlink
  if [ -f "$ZSHRC_FILE" ] && [ ! -L "$ZSHRC_FILE" ]; then
    TS=$(date +%s)
    echo "Backing up existing .zshrc to .zshrc.backup.$TS"
    cp "$ZSHRC_FILE" "$ZSHRC_FILE.backup.$TS"
  fi

  {
    echo "# [DOTFILES] Load custom configuration"
    echo "source \"$INIT_FILE\""
    echo ""
    echo "# [SYSTEM] Other tools can append configuration below:"
  } >"$ZSHRC_FILE"
  echo "New entry point generated."
fi

# --- 8. Local-only config file ---
# We agree that the personalized configuration file is named .zshrc.local
if [ ! -f "$HOME/.zshrc.local" ]; then
  echo "no local config found, creating an empty ~/.zshrc.local"
  touch "$HOME/.zshrc.local"
else
  echo "found ~/.zshrc.local, keeping the existing one"
fi

echo "Zsh environment setup complete! Please restart your terminal or run 'source ~/.zshrc' to apply the changes."
