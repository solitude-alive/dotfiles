# Python Configuration

Personal Python development environment setup, powered by [uv](https://github.com/astral-sh/uv) and [Ruff](https://github.com/astral-sh/ruff).

## What It Does

This setup will configure your Python development environment with the following:

1. **uv**: A fast Python package manager, used to manage global tools
2. **Global Tools** (installed via `uv tool`):
   - `ruff`: An extremely fast Python linter & formatter (replaces Flake8 + Black + isort)
   - `pre-commit`: A framework for managing Git pre-commit hooks
3. **Global Ruff Configuration**: A curated `ruff.toml` linked to `~/.config/ruff/ruff.toml`, governing personal scripts and non-project Python files
4. **Project Templates**: Ready-to-use `pyproject.toml` and `pre-commit-config.yaml` templates for new projects

## Installation

Run the installation script from this directory:

```bash
./install.sh
```

The script will:
- Install or update `uv` (smart detection for Homebrew-managed installs)
- Install or upgrade `ruff` and `pre-commit` as global tools
- Create a symbolic link for `ruff.toml` at `~/.config/ruff/ruff.toml`

**Note**: Existing configuration files will be automatically backed up with a timestamp before being replaced.

## Files

- `install.sh`: Installation script that sets up everything automatically
- `ruff.toml`: Global Ruff configuration (target Python 3.13+, line-length 100, curated rule set)
- `template/pyproject.toml`: A starter `pyproject.toml` with Ruff, Pytest, and Pyright configurations
- `template/pre-commit-config.yaml`: A starter pre-commit config with hygiene checks, shell linting, and Ruff hooks

## Ruff Rules Overview

The global `ruff.toml` enables a "Best Practice" rule collection:

| Rule   | Description                                          |
|--------|------------------------------------------------------|
| `E/W`  | pycodestyle errors & warnings (PEP 8)                |
| `F`    | Pyflakes (undefined variables, unused imports, etc.) |
| `I`    | isort (automatic import sorting)                     |
| `B`    | flake8-bugbear (likely bugs & design problems)       |
| `UP`   | pyupgrade (auto-upgrade syntax to modern Python)     |
| `N`    | pep8-naming (naming conventions)                     |
| `SIM`  | flake8-simplify (simplify logic)                     |
| `RUF`  | Ruff-specific rules                                  |
| `C4`   | flake8-comprehensions (optimize comprehensions)      |

## Using Templates

Copy the templates into your new project as a starting point:

```bash
cp python/template/pyproject.toml /path/to/your/project/pyproject.toml
cp python/template/pre-commit-config.yaml /path/to/your/project/.pre-commit-config.yaml
```

Then customize them to fit your project's needs.
