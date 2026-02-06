# Zsh Configuration

Personal Zsh shell configuration with Oh My Zsh, Powerlevel10k theme, and useful plugins.

## What It Does

This setup will configure your Zsh environment with the following:

1. **Oh My Zsh**: A delightful framework for managing your Zsh configuration
2. **Powerlevel10k Theme**: A fast and highly customizable Zsh theme with a beautiful powerline prompt
3. **Plugins**:
   - `git`: Git aliases and functions
   - `zsh-autosuggestions`: Fish-like autosuggestions for Zsh
   - `zsh-syntax-highlighting`: Syntax highlighting for commands
4. **Custom Aliases**: Common command shortcuts defined in `.zsh_aliases`
5. **Local Configuration**: Support for machine-specific settings via `.zshrc.local`

## Installation

Run the installation script from this directory:

```bash
./install.sh
```

The script will:
- Install Oh My Zsh (if not already installed)
- Download Powerlevel10k theme
- Install zsh-autosuggestions and zsh-syntax-highlighting plugins
- Create symbolic links for `.zsh_aliases` and `.p10k.zsh` in your home directory
- Update `~/.zshrc` to source the custom `init.zsh` configuration
- Create an empty `~/.zshrc.local` file for your local customizations

**Note**: Existing configuration files will be automatically backed up with a timestamp before being replaced.

## Files

- `init.zsh`: Main Zsh configuration entry point, loaded by `~/.zshrc`
- `.zsh_aliases`: Custom command aliases
- `.p10k.zsh`: Powerlevel10k theme configuration
- `install.sh`: Installation script that sets up everything automatically

## Customization

For machine-specific or personal settings, edit `~/.zshrc.local`. This file is sourced automatically and won't be tracked in the repository.

## Applying Changes

After installation or making changes, restart your terminal or run:

```bash
source ~/.zshrc
```
