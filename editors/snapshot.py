"""snapshot: live config -> repo.   check: report drift (no writes)."""

import argparse

from core import (
    COPY_FILES,
    EDITORS,
    HOME,
    REPO,
    live_extensions,
    read_copy,
    redacted_settings_data,
    user_dir,
)
from sync import (
    SyncResult,
    sync_json_object,
    sync_line_set,
    sync_text,
    sync_tree,
)


def snapshot(args: argparse.Namespace) -> int:
    changed = False
    wrote = False

    def track(result: SyncResult) -> None:
        nonlocal changed, wrote
        changed |= result.changed
        wrote |= result.wrote

    for name, (support, extdir, _cli) in EDITORS.items():
        if args.editor and args.editor != name:
            continue
        src, dst = user_dir(support), REPO / name
        if not src.is_dir():
            print(f"  [{name}] not installed, skipping")
            continue
        print(f"  [{name}] {src}")

        if (src / "settings.json").is_file():
            settings = redacted_settings_data(src / "settings.json")
            if settings is None:
                print("    settings.json is not valid JSON, skipping")
            else:
                track(
                    sync_json_object(
                        "settings.json",
                        dst / "settings.json",
                        settings,
                        args,
                        current_label="repo",
                        target_label="live",
                    )
                )
        else:
            track(
                sync_text(
                    "settings.json",
                    dst / "settings.json",
                    None,
                    args,
                    current_label="repo",
                    target_label="live",
                )
            )

        for fname in COPY_FILES:
            target = read_copy(src / fname) if (src / fname).is_file() else None
            track(
                sync_text(
                    fname,
                    dst / fname,
                    target,
                    args,
                    current_label="repo",
                    target_label="live",
                )
            )

        track(
            sync_tree(
                "snippets/",
                src / "snippets",
                dst / "snippets",
                args,
                current_label="repo",
                target_label="live",
            )
        )

        ext_json = HOME / extdir / "extensions" / "extensions.json"
        exts = live_extensions(extdir)
        if exts is None and ext_json.is_file():
            print("    extensions.json is not valid JSON, skipping")
        else:
            track(
                sync_line_set(
                    "extensions.txt",
                    dst / "extensions.txt",
                    exts,
                    args,
                    current_label="repo",
                    target_label="live",
                    item_name="id",
                )
            )

    if args.dry_run:
        print("Dry run complete. No files written.")
    elif wrote:
        print("Done. Review accepted changes with: git diff editors/")
    elif changed:
        print("No files written.")
    else:
        print("No snapshot changes.")
    return 0
