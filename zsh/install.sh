#!/bin/bash

# get current dir (i.e., dotfiles/zsh)
CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ZSH_CUSTOM="${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}"

echo "Starting Zsh environment setup..."

# --- 1. install Oh My Zsh ---
if [ ! -d "$HOME/.oh-my-zsh" ]; then
    echo "cloning Oh My Zsh..."
    # Use --unattended to avoid entering zsh immediately after installation, which can interrupt the script
    sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
else
    echo "Oh My Zsh is already installed"
fi

# --- 2. download themes powerlevel10k ---
if [ ! -d "$ZSH_CUSTOM/themes/powerlevel10k" ]; then
    echo "downloading Powerlevel10k theme..."
    git clone --depth=1 https://github.com/romkatv/powerlevel10k.git "$ZSH_CUSTOM/themes/powerlevel10k"
else
    echo "Powerlevel10k theme is already installed"
fi

# --- 3. download plugins ---
echo "Installing/updating plugins..."
# Plugin: Auto Suggestions
if [ ! -d "$ZSH_CUSTOM/plugins/zsh-autosuggestions" ]; then
    git clone https://github.com/zsh-users/zsh-autosuggestions "$ZSH_CUSTOM/plugins/zsh-autosuggestions"
fi

# Plugin: Syntax Highlighting
if [ ! -d "$ZSH_CUSTOM/plugins/zsh-syntax-highlighting" ]; then
    git clone https://github.com/zsh-users/zsh-syntax-highlighting.git "$ZSH_CUSTOM/plugins/zsh-syntax-highlighting"
fi

# --- 4. link common configuration files ---
echo "Linking common configuration files..."

# backup existing .zshrc if it's not a symlink
if [ -f "$HOME/.zshrc" ] && [ ! -L "$HOME/.zshrc" ]; then
    echo "Backing up existing .zshrc to .zshrc.pre-dotfiles.TIMESTAMP"
    mv "$HOME/.zshrc" "$HOME/.zshrc.pre-dotfiles.$(date +%s)"
fi
# backup .zsh_aliases
if [ -f "$HOME/.zsh_aliases" ] && [ ! -L "$HOME/.zsh_aliases" ]; then
    echo "Backing up existing .zsh_aliases to .zsh_aliases.backup.TIMESTAMP"
    mv "$HOME/.zsh_aliases" "$HOME/.zsh_aliases.backup.$(date +%s)"
fi
# backup .p10k.zsh
if [ -f "$HOME/.p10k.zsh" ] && [ ! -L "$HOME/.p10k.zsh" ]; then
    mv "$HOME/.p10k.zsh" "$HOME/.p10k.zsh.backup.$(date +%s)"
fi

## Create a symlink to use the common configuration from your repository
ln -sf "$CURRENT_DIR/.zshrc" "$HOME/.zshrc"
ln -sf "$CURRENT_DIR/.zsh_aliases" "$HOME/.zsh_aliases"
ln -sf "$CURRENT_DIR/.p10k.zsh" "$HOME/.p10k.zsh"

# --- 5. (local specific) ---
# We agree that the personalized configuration file is named .zshrc.local
if [ ! -f "$HOME/.zshrc.local" ]; then
    echo "no local config found, creating an empty ~/.zshrc.local"
    touch "$HOME/.zshrc.local"
else
    echo "found ~/.zshrc.local, keeping the existing one"
fi

echo "Zsh environment setup complete! Please restart your terminal or run 'source ~/.zshrc' to apply the changes."
