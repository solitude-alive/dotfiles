# shellcheck shell=bash

# --- 1. setting  ---
# shellcheck disable=SC1091
if [ -f "$HOME/.p10k.zsh" ]; then
    source "$HOME/.p10k.zsh"
fi

export ZSH="$HOME/.oh-my-zsh"

# --- 2. theme (need download p10k first) ---
# shellcheck disable=SC2034
ZSH_THEME="powerlevel10k/powerlevel10k"

# --- 3. plugins----
# shellcheck disable=SC2034
plugins=(
    git
    zsh-autosuggestions
    zsh-syntax-highlighting
)

source "$ZSH/oh-my-zsh.sh"

# --- 4. load local config (optional) ---
if [ -f ~/.zshrc.local ]; then
    source "$HOME/.zshrc.local"
else
    echo "no local config found ('$HOME/.zshrc.local'), skipping..."
fi

# --- 5. aliases if [ -f ~/.zsh_aliases ] ---
if [ -f ~/.zsh_aliases ]; then
    source "$HOME/.zsh_aliases"
else
    echo "no aliases file found ('$HOME/.zsh_aliases'), skipping..."
fi

# You can add more custom configurations below
