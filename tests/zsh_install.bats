#!/usr/bin/env bats
# Integration tests for zsh/install.sh.
#
# These tests verify the platform-specific linking behaviour we rely
# on (mac vs linux config files), idempotency, and error paths.
# Designed to run on GitHub Actions matrix (ubuntu + macos). Each
# test gets a fresh $HOME so the runner is not polluted.

load 'helpers/setup_suite.bash'

setup() {
  setup_test_home
  REPO_ROOT="$(repo_root)"
  cd "$REPO_ROOT" || exit 1
}

teardown() {
  teardown_test_home
}

# ---------------------------------------------------------------
# Platform-specific linking (the core contract of this refactor)
# ---------------------------------------------------------------

@test "links the correct aliases file for the current platform" {
  run ./zsh/install.sh
  [ "$status" -eq 0 ]
  [ -L "$HOME/.zsh_aliases" ]

  target="$(readlink "$HOME/.zsh_aliases")"
  if [[ "$OSTYPE" == darwin* ]]; then
    [[ "$target" == *"/zsh/.zsh_aliases.mac" ]]
  else
    [[ "$target" == *"/zsh/.zsh_aliases.linux" ]]
  fi
}

@test "links the correct p10k file for the current platform" {
  run ./zsh/install.sh
  [ "$status" -eq 0 ]
  [ -L "$HOME/.p10k.zsh" ]

  target="$(readlink "$HOME/.p10k.zsh")"
  if [[ "$OSTYPE" == darwin* ]]; then
    [[ "$target" == *"/zsh/.p10k.mac.zsh" ]]
  else
    [[ "$target" == *"/zsh/.p10k.linux.zsh" ]]
  fi
}

# ---------------------------------------------------------------
# .zshrc / .zshrc.local generation
# ---------------------------------------------------------------

@test "creates ~/.zshrc that sources init.zsh" {
  run ./zsh/install.sh
  [ "$status" -eq 0 ]
  [ -f "$HOME/.zshrc" ]
  grep -Fq "init.zsh" "$HOME/.zshrc"
}

@test "creates an empty ~/.zshrc.local if missing" {
  run ./zsh/install.sh
  [ "$status" -eq 0 ]
  [ -f "$HOME/.zshrc.local" ]
}

@test "preserves existing ~/.zshrc.local contents" {
  mkdir -p "$HOME"
  echo "export LOCAL_MARKER=1" >"$HOME/.zshrc.local"

  run ./zsh/install.sh
  [ "$status" -eq 0 ]
  grep -Fq "LOCAL_MARKER=1" "$HOME/.zshrc.local"
}

# ---------------------------------------------------------------
# Idempotency & recovery
# ---------------------------------------------------------------

@test "is idempotent (two consecutive runs both succeed)" {
  run ./zsh/install.sh
  [ "$status" -eq 0 ]

  run ./zsh/install.sh
  [ "$status" -eq 0 ]

  [ -L "$HOME/.zsh_aliases" ]
  [ -L "$HOME/.p10k.zsh" ]
}

@test "heals a broken .zsh_aliases symlink on re-run" {
  # First run sets up proper links.
  run ./zsh/install.sh
  [ "$status" -eq 0 ]

  # Simulate a stale/broken symlink (e.g. after renaming files in repo).
  rm "$HOME/.zsh_aliases"
  ln -s /nonexistent/path "$HOME/.zsh_aliases"

  run ./zsh/install.sh
  [ "$status" -eq 0 ]
  # -e follows the symlink; passes only if target actually exists.
  [ -e "$HOME/.zsh_aliases" ]
}

@test "backs up a pre-existing real ~/.zsh_aliases file" {
  mkdir -p "$HOME"
  echo "# user content that must not be lost" >"$HOME/.zsh_aliases"

  run ./zsh/install.sh
  [ "$status" -eq 0 ]

  # Original content must survive in a backup file.
  backup="$(find "$HOME" -maxdepth 1 -name '.zsh_aliases.backup.*' -print -quit)"
  [ -n "$backup" ]
  grep -Fq "user content that must not be lost" "$backup"

  # Live file should now be a symlink to the repo version.
  [ -L "$HOME/.zsh_aliases" ]
}

# ---------------------------------------------------------------
# Error paths
# ---------------------------------------------------------------

@test "exits non-zero when the platform p10k file is missing" {
  if [[ "$OSTYPE" == darwin* ]]; then
    platform_file="zsh/.p10k.mac.zsh"
  else
    platform_file="zsh/.p10k.linux.zsh"
  fi
  hidden="${platform_file}.hidden_for_test"

  mv "$platform_file" "$hidden"
  run ./zsh/install.sh
  status_code="$status"
  # Always restore BEFORE asserting, so a failure doesn't leave the
  # working tree broken on a dev's machine if they ran this locally.
  mv "$hidden" "$platform_file"

  [ "$status_code" -ne 0 ]
}
