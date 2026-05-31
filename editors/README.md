# editors

Read-only **audit snapshot** of VS Code and Cursor config. Nothing here is
symlinked or written back to the editors — live syncing is left to each
editor's Settings Sync. This repo exists so `git log` is the audit trail.

## What's captured

`settings.json`, `keybindings.json`, `tasks.json`, snippets, and the extension
id list. Binary/ephemeral state (`state.vscdb`, UI layout, profiles) is left to
Settings Sync. See `annotations.md` for what each key means.

VS Code and Cursor sync to separate clouds, so this is also the only place
their configs sit side by side.

## Layout

```
editors/
├── snapshot.sh   # capture live config into the repo (editor -> repo)
├── check.sh      # report drift between repo and live
├── annotations.md
├── vscode/   settings.json, extensions.txt
└── cursor/   settings.json, keybindings.json, extensions.txt
```

## Usage

```bash
./snapshot.sh        # refresh, then: git diff editors/
./check.sh           # exit 0 = in sync, 1 = drift (pre-commit/CI friendly)
```

Notes: extension lists store ids only; `remote.SSH.remotePlatform` is redacted
(internal host names); requires `python3`.
