"""snapshot: live config -> repo.   check: report drift (no writes)."""

import argparse

from core import (
    COPY_FILES,
    EDITORS,
    HOME,
    REPO,
    live_extensions,
    read,
    read_copy,
    redacted_settings,
    user_dir,
)
from syncutil import show_diff, sync_text, sync_tree


def compare(label: str, repo: str | None, live: str | None) -> bool:
    """True if drift; prints status and diff on mismatch."""
    if repo is None and live is None:
        return False
    if repo is None:
        print(f"    DRIFT {label}: live exists but not snapshotted")
        return True
    if live is None:
        print(f"    DRIFT {label}: snapshotted but missing live")
        return True
    if repo != live:
        print(f"    DRIFT {label}:")
        show_diff(live, repo)
        return True
    print(f"    ok    {label}")
    return False


def snapshot(args: argparse.Namespace) -> int:
    changed = False
    wrote = False
    for name, (support, extdir, _cli) in EDITORS.items():
        if args.editor and args.editor != name:
            continue
        src, dst = user_dir(support), REPO / name
        if not src.is_dir():
            print(f"  [{name}] not installed, skipping")
            continue
        print(f"  [{name}] {src}")

        if (src / "settings.json").is_file():
            settings = redacted_settings(src / "settings.json")
            if settings is None:
                print("    settings.json is not valid JSON, skipping")
            else:
                found, done = sync_text(
                    "settings.json",
                    dst / "settings.json",
                    settings,
                    args,
                    current_label="repo",
                    target_label="live",
                )
                changed |= found
                wrote |= done
        else:
            found, done = sync_text(
                "settings.json",
                dst / "settings.json",
                None,
                args,
                current_label="repo",
                target_label="live",
            )
            changed |= found
            wrote |= done

        for fname in COPY_FILES:
            target = read_copy(src / fname) if (src / fname).is_file() else None
            found, done = sync_text(
                fname,
                dst / fname,
                target,
                args,
                current_label="repo",
                target_label="live",
            )
            changed |= found
            wrote |= done

        found, done = sync_tree(
            "snippets/",
            src / "snippets",
            dst / "snippets",
            args,
            current_label="repo",
            target_label="live",
        )
        changed |= found
        wrote |= done

        ext_json = HOME / extdir / "extensions" / "extensions.json"
        exts = live_extensions(extdir)
        if exts is None and ext_json.is_file():
            print("    extensions.json is not valid JSON, skipping")
        else:
            found, done = sync_text(
                "extensions.txt",
                dst / "extensions.txt",
                exts,
                args,
                current_label="repo",
                target_label="live",
            )
            changed |= found
            wrote |= done

    if args.dry_run:
        print("Dry run complete. No files written.")
    elif wrote:
        print("Done. Review accepted changes with: git diff editors/")
    elif changed:
        print("No files written.")
    else:
        print("No snapshot changes.")
    return 0


def check() -> int:
    drift = False
    for name, (support, extdir, _cli) in EDITORS.items():
        src = user_dir(support)
        print(f"== {name} ==")
        if not src.is_dir():
            print("    (not installed, skipping)")
            continue
        live_s = (
            redacted_settings(src / "settings.json") if (src / "settings.json").is_file() else None
        )
        drift |= compare("settings.json", read(REPO / name / "settings.json"), live_s)
        for fname in COPY_FILES:
            drift |= compare(fname, read(REPO / name / fname), read_copy(src / fname))
        drift |= compare(
            "extensions.txt", read(REPO / name / "extensions.txt"), live_extensions(extdir)
        )
    print()
    if drift:
        print("Drift detected. Run ./editors.sh snapshot to refresh.")
        return 1
    print("No drift: snapshot matches live config.")
    return 0
