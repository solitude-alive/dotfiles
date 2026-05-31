# Annotations

What each captured key means. Raw JSON stays comment-free so diffs stay clean.

## vscode/settings.json

| key | value | meaning |
|-----|-------|---------|
| `files.autoSave` | `afterDelay` | auto-save after a short delay |
| `update.showReleaseNotes` | `false` | hide extension/product release notes popups |
| `github.copilot.chat.edits.temporalContext.enabled` | `true` | Copilot edits can use temporal context |
| `chatgpt.composerEnterBehavior` | `enter` | Enter sends in ChatGPT Composer |

## cursor/settings.json

| key | value | meaning |
|-----|-------|---------|
| `workbench.editorAssociations` | `{}` | file→editor map; empty = default |
| `workbench.activityBar.orientation` | `vertical` | activity bar orientation |
| `remote.SSH.remotePlatform` | — | ignored via `ignore.json` (internal host names) |
| `gitlens.ai.*.model` | — | ignored via `ignore.json` (provider/model choice changes often) |
| `gitlens.modes` | — | ignored via `ignore.json` (generated GitLens mode defaults) |
| `files.autoSave` | `afterDelay` | auto-save after a delay |
| `remote.autoForwardPortsSource` | `hybrid` | port auto-forward detection (process + output) |
| `[python]` | object | Python: keep diff whitespace, no inline color chips |
| `cursor.cpp.enablePartialAccepts` | `true` | accept partial autocomplete |
| `cursor.cpp.disabledLanguages` | `["plaintext"]` | no tab-completion in plaintext |
| `editor.formatOnSave` | `true` | format on save |
| `terminal.integrated.env.linux` | `{}` | extra terminal env (Linux); none |
| `[shellscript]` | object | shell: force LF, no inline color chips |
| `claudeCode.preferredLocation` | `panel` | Claude Code UI docked in panel |
| `claudeCode.environmentVariables` | `[]` | extra Claude Code env; none |
| `window.autoDetectColorScheme` | `false` | don't follow OS light/dark |

## cursor/keybindings.json

| key | command | meaning |
|-----|---------|---------|
| `cmd+i` | `composerMode.agent` | open Composer in Agent mode |
| `alt+tab` | `markdown.extension.onTabKey` | rebind markdown "Tab in list" to alt+tab |
| `tab` | `-markdown.extension.onTabKey` | leading `-` removes the default Tab binding |

## Extensions

Ids live in `vscode/extensions.txt` (15) and `cursor/extensions.txt` (19); the
ids are self-describing. Cursor-only additions: `anysphere.cursorpyright`,
`anysphere.remote-ssh`, `ms-python.mypy-type-checker`, `ms-python.pylint`,
`timonwong.shellcheck`, `yzhang.markdown-all-in-one`, `donjayamanne.githistory`,
`ms-azuretools.vscode-docker`.

## Applying (apply.sh)

`apply.sh` writes the repo back onto a machine (repo → editor) as a **clean
mirror**: repo-tracked keys win, ignored settings/extensions in `ignore.json`
are preserved verbatim, and any extra keys / files / extensions not in the repo
or ignore list are reviewed for removal (default keep; `--force` removes).
Live files are backed up to `<file>.backup.<timestamp>` first. This keeps
the apply ↔ snapshot loop drift-free: after `apply.sh --force`, a fresh snapshot
matches the repo.

## Not captured

Binary/ephemeral state (`state.vscdb`, `workspaceStorage/`, `History/`, UI
layout, profiles) is left to Settings Sync. `argv.json` (machine-level, not
synced) and empty files (`mcp.json`, snippets, tasks) are skipped.
