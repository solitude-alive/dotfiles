# editors

**Audit snapshot** of VS Code and Cursor config, plus an explicit **apply** path.
`snapshot`/`check` only read the editors (editor → repo) so `git log` is the audit
trail; nothing is symlinked, and live syncing is still left to each editor's
Settings Sync. The only writes back to an editor happen when you run `apply`
(repo → editor), which always backs up first.

## What's captured

`settings.json`, `keybindings.json`, `tasks.json`, snippets, and the extension id
list. Binary/ephemeral state (`state.vscdb`, UI layout, profiles) is left to
Settings Sync. See `annotations.md` for what each key means.

VS Code and Cursor sync to separate clouds, so this is also the only place their
configs sit side by side.

## Layout

```
editors/
├── editors.sh    # wrapper -> editors.py
├── editors.py    # entry: snapshot | check | apply
├── core.py       # shared helpers (paths, json, ignore, backup)
├── snapshot.py   # snapshot + check
├── apply.py      # apply (clean mirror)
├── diffutil.py   # diff output
├── annotations.md
├── vscode/   settings.json, extensions.txt
└── cursor/   settings.json, keybindings.json, extensions.txt
```

## Usage

```bash
./editors.sh snapshot          # refresh repo from this machine, then: git diff editors/
./editors.sh check             # exit 0 = in sync, 1 = drift (pre-commit/CI friendly)
./editors.sh apply             # interactive: review each diff, then write (repo -> editor)
./editors.sh apply --dry-run   # show what would change, write nothing
./editors.sh apply --force     # no prompts; make this machine a clean mirror
./editors.sh apply cursor      # restrict to one editor (vscode | cursor)
```

`apply` builds a **clean mirror**: repo-tracked keys/files win, machine-local keys
in IGNORE (`remote.SSH.remotePlatform`) are kept, and anything extra (keys, files,
extensions not in the repo) is offered for removal. Live files are backed up to
`<file>.backup.<timestamp>` before any write; extensions install/uninstall via the
editor CLI.

Notes: extension lists store ids only; `remote.SSH.remotePlatform` is redacted
(internal host names); requires `python3`.
