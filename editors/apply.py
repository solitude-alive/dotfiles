"""apply: repo -> this machine, as a clean mirror (backs up before writing)."""

import argparse
import shutil
import subprocess

from core import (
    COPY_FILES,
    EDITORS,
    IGNORE,
    REPO,
    backup,
    dump_settings,
    live_extensions,
    load_json,
    user_dir,
)
from syncutil import approve, sync_text, sync_tree


def apply_settings(src, dst, args) -> None:
    live, repo = load_json(dst) or {}, load_json(src) or {}
    preserved = {k: live[k] for k in IGNORE if k in live}
    target = dump_settings({**preserved, **repo})  # repo wins, IGNORE kept
    sync_text(
        "settings.json",
        dst,
        target,
        args,
        current_label="live",
        target_label="repo",
        before_change=backup,
    )


def apply_files(src_dir, dst_dir, args) -> None:
    for fname in COPY_FILES:
        rp, lp = src_dir / fname, dst_dir / fname
        target = rp.read_text() if rp.is_file() else None
        sync_text(
            fname,
            lp,
            target,
            args,
            current_label="live",
            target_label="repo",
            remove_desc=f"remove extra {fname}",
            before_change=backup,
        )


def apply_snippets(src_dir, dst_dir, args) -> None:
    sync_tree(
        "snippets/",
        src_dir,
        dst_dir,
        args,
        current_label="live",
        target_label="repo",
        remove_desc="remove extra snippets/",
        before_change=backup,
    )


def apply_extensions(cli, listfile, extdir, args) -> None:
    repo_ids = (
        {x.strip() for x in listfile.read_text().splitlines() if x.strip()}
        if listfile.is_file()
        else set()
    )
    live_ids = set((live_extensions(extdir) or "").split())
    to_install = sorted(repo_ids - live_ids)
    to_remove = sorted(live_ids - repo_ids)
    if not to_install and not to_remove:
        return
    if args.dry_run:
        for ext in to_install:
            approve(f"install {ext}", args)
        for ext in to_remove:
            approve(f"uninstall extra {ext}", args)
        return
    exe = shutil.which(cli)
    if not exe:
        print(
            f"    '{cli}' CLI not found; skip {len(to_install)} install / {len(to_remove)} remove"
        )
        return
    for ext in to_install:
        if approve(f"install {ext}", args):
            subprocess.run(
                [exe, "--install-extension", ext, "--force"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
    for ext in to_remove:
        if approve(f"uninstall extra {ext}", args):
            subprocess.run(
                [exe, "--uninstall-extension", ext],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )


def apply(args: argparse.Namespace) -> int:
    for name, (support, extdir, cli) in EDITORS.items():
        if args.editor and args.editor != name:
            continue
        src, dst = REPO / name, user_dir(support)
        if not src.is_dir():
            print(f"  [{name}] no snapshot in repo, skipping")
            continue
        dst.mkdir(parents=True, exist_ok=True)
        print(f"  [{name}] -> {dst}")
        if (src / "settings.json").is_file():
            apply_settings(src / "settings.json", dst / "settings.json", args)
        apply_files(src, dst, args)
        apply_snippets(src / "snippets", dst / "snippets", args)
        apply_extensions(cli, src / "extensions.txt", extdir, args)
    return 0
