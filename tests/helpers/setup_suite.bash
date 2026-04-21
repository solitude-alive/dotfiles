#!/usr/bin/env bash
# Shared helpers for bats integration tests.
#
# These helpers redirect $HOME to a disposable temp dir and stub out
# network-heavy / interactive parts of install.sh so tests stay fast
# and don't pollute the runner.
#
# WARNING: these tests are designed for ephemeral CI runners. Running
# them locally will temporarily modify the repo working tree in some
# cases (e.g. tests that rename platform files to assert error paths).

# Create an isolated $HOME and pre-seed directories so install.sh
# skips git-clone / curl-pipe steps (Oh My Zsh, p10k theme, plugins).
setup_test_home() {
  export TEST_HOME
  TEST_HOME="$(mktemp -d)"
  export HOME="$TEST_HOME"

  # Pre-create OMZ + p10k theme + plugin dirs so the corresponding
  # `if [ ! -d ... ]` branches in zsh/install.sh are skipped.
  mkdir -p "$HOME/.oh-my-zsh/custom/themes/powerlevel10k"
  mkdir -p "$HOME/.oh-my-zsh/custom/plugins/zsh-autosuggestions"
  mkdir -p "$HOME/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting"

  # Make the "is zsh the default shell?" check a no-op so chsh is
  # never invoked (chsh requires PAM/sudo and hangs in CI).
  if command -v zsh >/dev/null 2>&1; then
    SHELL="$(command -v zsh)"
    export SHELL
  fi
}

teardown_test_home() {
  if [[ -n "${TEST_HOME:-}" && -d "$TEST_HOME" ]]; then
    rm -rf "$TEST_HOME"
  fi
  unset TEST_HOME
}

# Return the absolute path to the repo root, regardless of where
# bats is invoked from.
repo_root() {
  # $BATS_TEST_DIRNAME is the directory of the currently running
  # .bats file (e.g. <repo>/tests). Two dirs up from helpers/ is root.
  (cd "$BATS_TEST_DIRNAME/.." && pwd)
}
