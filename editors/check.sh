#!/bin/bash
# Report drift between the repo snapshot and live editor config.
# Exit 0 = in sync, 1 = drift. See README.md.

set -uo pipefail
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

DRIFT=0

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

# Must match snapshot.sh's filter_settings exactly.
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

compare() { # <label> <repo-file> <live-file>
  local label="$1" repo="$2" live="$3"
  if [ ! -e "$repo" ] && [ ! -e "$live" ]; then
    return 0
  elif [ ! -e "$repo" ]; then
    echo "    DRIFT $label: live exists but NOT snapshotted"
    DRIFT=1
  elif [ ! -e "$live" ]; then
    echo "    DRIFT $label: snapshotted but missing live"
    DRIFT=1
  elif ! diff -q "$repo" "$live" >/dev/null 2>&1; then
    echo "    DRIFT $label:"
    diff -u "$repo" "$live" 2>/dev/null | sed 's/^/      /'
    DRIFT=1
  else
    echo "    ok    $label"
  fi
}

check_editor() {
  local name="$1" support="$2" extdir="$3"
  local src="$CFG/$support/User"
  echo "== $name =="
  if [ ! -d "$src" ]; then
    echo "    (not installed, skipping)"
    return 0
  fi

  # settings.json: compare against a redacted copy of live (mirrors snapshot.sh).
  if [ -f "$src/settings.json" ]; then
    local tmp_s
    tmp_s="$(mktemp)"
    filter_settings "$src/settings.json" >"$tmp_s"
    compare "settings.json" "$ROOT/$name/settings.json" "$tmp_s"
    rm -f "$tmp_s"
  else
    compare "settings.json" "$ROOT/$name/settings.json" "$src/settings.json"
  fi

  local f
  for f in keybindings.json tasks.json; do
    compare "$f" "$ROOT/$name/$f" "$src/$f"
  done

  local ext_json="$HOME/$extdir/extensions/extensions.json"
  if [ -f "$ext_json" ]; then
    local tmp
    tmp="$(mktemp)"
    list_extensions "$ext_json" >"$tmp"
    compare "extensions.txt" "$ROOT/$name/extensions.txt" "$tmp"
    rm -f "$tmp"
  fi
}

echo "Checking snapshot vs live editor config..."
check_editor "vscode" "Code" ".vscode"
check_editor "cursor" "Cursor" ".cursor"

echo
if [ "$DRIFT" -eq 0 ]; then
  echo "No drift: snapshot matches live config."
else
  echo "Drift detected. Run ./snapshot.sh to refresh."
  exit 1
fi
