# Dotfiles
Personal configuration files for various applications and tools.

## Installation
To set up these dotfiles on your system, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/solitude-alive/dotfiles.git
    ```
2. Navigate to the cloned directory:
    ```bash
    cd dotfiles
    ```
3. Run the installation script:
    ```bash
    ./install.sh
    ```

This script will create symbolic links for the configuration files in your home directory.

## Explanation of Files
- `zsh`: Zsh shell configuration, including themes and plugins.

## pre-commit

This repository uses `pre-commit` to manage and run pre-commit hooks. To set it up, follow these steps:
1. Install `pre-commit` if you haven't already. You can do this using pip:
    ```bash
    pip install pre-commit
    ```
2. Install the pre-commit hooks defined in the `.pre-commit-config.yaml` file:
    ```bash
    pre-commit install
    ```
3. To run the pre-commit hooks manually on all files, use:
    ```bash
    pre-commit run --all-files
    ```
4. To update the pre-commit hooks to their latest versions, use:
    ```bash
    pre-commit autoupdate
    ```
