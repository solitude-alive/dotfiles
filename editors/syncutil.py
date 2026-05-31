"""Shared sync primitives for text files and small config trees."""

import argparse
import difflib
import shutil
import sys
from collections.abc import Callable
from pathlib import Path

from core import read

BeforeChange = Callable[[Path], None]


def show_diff(
    current: str | None,
    target: str,
    current_label: str = "live",
    target_label: str = "repo",
) -> None:
    diff = difflib.unified_diff(
        (current or "").splitlines(True),
        target.splitlines(True),
        current_label,
        target_label,
    )
    for line in diff:
        sys.stdout.write("      " + line)
        if not line.endswith("\n"):
            sys.stdout.write("\n")


def approve(desc: str, args: argparse.Namespace) -> bool:
    if args.dry_run:
        print(f"    [dry-run] would {desc}")
        return False
    if args.force:
        print(f"    {desc}")
        return True
    return input(f"    {desc}? [y/N] ").strip().lower() in ("y", "yes")


def remove_path(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def sync_text(
    label: str,
    dst: Path,
    target: str | None,
    args: argparse.Namespace,
    *,
    current_label: str,
    target_label: str,
    write_desc: str | None = None,
    remove_desc: str | None = None,
    before_change: BeforeChange | None = None,
) -> tuple[bool, bool]:
    """Sync one text file. Returns (changed, wrote)."""
    current = read(dst)
    if target is None:
        if current is None:
            return False, False
        print(f"    CHANGE {label}:")
        show_diff(current, "", current_label, target_label)
        if approve(remove_desc or f"remove {label}", args):
            if before_change:
                before_change(dst)
            remove_path(dst)
            return True, True
        return True, False

    if current == target:
        return False, False

    print(f"    CHANGE {label}:")
    show_diff(current, target, current_label, target_label)
    if approve(write_desc or f"write {label}", args):
        if before_change:
            before_change(dst)
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(target)
        return True, True
    return True, False


def rel_files(root: Path) -> set[Path]:
    if not root.is_dir():
        return set()
    return {p.relative_to(root) for p in root.rglob("*") if p.is_file()}


def rel_entries(root: Path) -> set[Path]:
    if not root.is_dir():
        return set()
    return {p.relative_to(root) for p in root.rglob("*")}


def has_tree(root: Path) -> bool:
    return root.is_dir() and any(root.iterdir())


def sync_tree(
    label: str,
    src: Path,
    dst: Path,
    args: argparse.Namespace,
    *,
    current_label: str,
    target_label: str,
    write_desc: str | None = None,
    remove_desc: str | None = None,
    before_change: BeforeChange | None = None,
) -> tuple[bool, bool]:
    """Sync a small directory tree. Returns (changed, wrote)."""
    if not has_tree(src):
        if not dst.exists():
            return False, False
        for rel in sorted(rel_files(dst)):
            print(f"    CHANGE {label}{rel}:")
            show_diff(read(dst / rel), "", current_label, target_label)
        if not rel_files(dst):
            print(f"    CHANGE {label}: {current_label} exists, {target_label} is absent")
        if approve(remove_desc or f"remove {label}", args):
            if before_change:
                before_change(dst)
            remove_path(dst)
            return True, True
        return True, False

    current_files = rel_files(dst)
    target_files = rel_files(src)
    changed = rel_entries(dst) != rel_entries(src)
    showed_file_diff = False
    for rel in sorted(current_files | target_files):
        current = read(dst / rel) if rel in current_files else None
        target = read(src / rel) if rel in target_files else ""
        if current != target:
            changed = True
            showed_file_diff = True
            print(f"    CHANGE {label}{rel}:")
            show_diff(current, target, current_label, target_label)
    if not changed:
        return False, False
    if not showed_file_diff:
        print(f"    CHANGE {label}: directory entries differ")

    if approve(write_desc or f"write {label}", args):
        if before_change:
            before_change(dst)
        remove_path(dst)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src, dst)
        return True, True
    return True, False
