# Python Configuration

Personal Python development environment setup, powered by [uv](https://github.com/astral-sh/uv) and [Ruff](https://github.com/astral-sh/ruff).

## What It Does

This setup will configure your Python development environment with the following:

1. **uv**: A fast Python package manager, used to manage global tools
2. **Global Tools** (installed via `uv tool`):
   - `ruff`: An extremely fast Python linter & formatter (replaces Flake8 + Black + isort)
   - `pre-commit`: A framework for managing Git pre-commit hooks
3. **Global Ruff Configuration**: A curated `ruff.toml` linked to `~/.config/ruff/ruff.toml`, governing personal scripts and non-project Python files
4. **Project Templates**: Ready-to-use `pyproject.toml`, `pre-commit-config.yaml`, and `ci.yaml` (GitHub Actions) templates for new projects

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
- `template/ci.yaml`: A GitHub Actions CI workflow that runs all pre-commit hooks on PRs and pushes

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
cp python/template/ci.yaml /path/to/your/project/.github/workflows/ci.yaml
```

Then customize them to fit your project's needs.

## Current Status

| Category | Tool | Status |
|----------|------|--------|
| Package Manager | uv | Installed & auto-updated via `install.sh` |
| Linter & Formatter | Ruff | Global config + project template + pre-commit hook + CI |
| Pre-commit Hooks | pre-commit | Template with hygiene, shell, and Ruff hooks |
| CI/CD | GitHub Actions | Runs all pre-commit hooks on PR/push |
| Testing | Pytest | Config in `pyproject.toml` template (CI job not yet added) |
| Type Checking | Pyright | Config in `pyproject.toml` template (CI job not yet added) |

## Future Considerations

Things to consider adding as the setup evolves:

- **CI: Test job** -- Add a `pytest` job to CI so tests run automatically on PR/push (pytest config is already in `pyproject.toml`)
- **CI: Type checking job** -- Add a `pyright` job to CI for static type checking (pyright config is already in `pyproject.toml`)
- **CI: Multi-version matrix** -- Test against multiple Python versions using `strategy.matrix`
- **Coverage reporting** -- Integrate `pytest-cov` and upload coverage reports (e.g., Codecov)
- **Dependency management template** -- Add a `requirements.txt` or `uv.lock` workflow template for reproducible installs
