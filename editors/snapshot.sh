#!/bin/bash
# Capture live editor config INTO this repo (editor -> repo, read-only).
# Never writes back, never symlinks. See README.md.

set -euo pipefail
cd "$(dirname "$0")" || exit 1
ROOT="$(pwd)"

case "$OSTYPE" in
darwin*) CFG="$HOME/Library/Application Support" ;;
linux*) CFG="$HOME/.config" ;;
*)
  echo "unsupported os: $OSTYPE" >&2
  exit 1
  ;;
esac

list_extensions() {
  [ -f "$1" ] || return 0
  python3 - "$1" <<'PY'
import json, sys
try:
    data = json.load(open(sys.argv[1]))
    print("\n".join(sorted({e["identifier"]["id"] for e in data})))
except Exception:
    pass
PY
}

# Emit settings.json with ignored keys removed. IGNORE must match check.sh.
filter_settings() {
  python3 - "$1" <<'PY'
import json, sys
IGNORE = {"remote.SSH.remotePlatform"}  # internal host names
try:
    data = json.load(open(sys.argv[1]))
except Exception:
    sys.exit(0)
for key in IGNORE:
    data.pop(key, None)
sys.stdout.write(json.dumps(data, indent=4, ensure_ascii=False) + "\n")
PY
}

# snapshot_editor <repo-subdir> <support-dir-name> <home-ext-dir>
snapshot_editor() {
  local name="$1" support="$2" extdir="$3"
  local src="$CFG/$support/User" dst="$ROOT/$name"

  if [ ! -d "$src" ]; then
    echo "  [$name] not installed, skipping."
    return 0
  fi
  mkdir -p "$dst"
  echo "  [$name] capturing from: $src"

  local f
  for f in settings.json keybindings.json tasks.json; do
    [ -f "$src/$f" ] || continue
    if [ "$f" = "settings.json" ]; then
      filter_settings "$src/$f" >"$dst/$f"
    else
      cp "$src/$f" "$dst/$f"
    fi
    echo "    + $f"
  done

  if [ -d "$src/snippets" ] && [ -n "$(ls -A "$src/snippets" 2>/dev/null)" ]; then
    rm -rf "$dst/snippets"
    cp -R "$src/snippets" "$dst/snippets"
    echo "    + snippets/"
  fi

  local ext_json="$HOME/$extdir/extensions/extensions.json"
  if [ -f "$ext_json" ]; then
    list_extensions "$ext_json" >"$dst/extensions.txt"
    echo "    + extensions.txt ($(wc -l <"$dst/extensions.txt" | tr -d ' ') ids)"
  fi
}

echo "Snapshotting editor configs..."
snapshot_editor "vscode" "Code" ".vscode"
snapshot_editor "cursor" "Cursor" ".cursor"
echo "Done. Review with: git diff editors/"
