"""Directory tree sync."""

import argparse
from pathlib import Path

from core import read

from .diff import print_change, show_diff
from .paths import (
    has_tree,
    rel_entries,
    rel_files,
    remove_path,
    replace_tree,
    tree_absent_or_empty,
)
from .prompt import approve
from .types import BeforeChange, DiffLabels, SyncResult


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
) -> SyncResult:
    """Sync a small directory tree."""
    labels = DiffLabels(current_label, target_label)
    if not has_tree(src):
        if tree_absent_or_empty(dst):
            return SyncResult()
        _show_removed_tree(label, dst, labels)
        if approve(remove_desc or f"remove {label}", args):
            remove_path(dst, before_change)
            return SyncResult(changed=True, wrote=True)
        return SyncResult(changed=True)

    changed = rel_entries(dst) != rel_entries(src)
    showed_file_diff = _show_tree_file_diffs(label, src, dst, labels)
    if not changed and not showed_file_diff:
        return SyncResult()
    if changed and not showed_file_diff:
        print_change(label, "directory entries differ")

    if approve(write_desc or f"write {label}", args):
        replace_tree(src, dst, before_change)
        return SyncResult(changed=True, wrote=True)
    return SyncResult(changed=True)


def _show_removed_tree(label: str, dst: Path, labels: DiffLabels) -> None:
    files = rel_files(dst)
    for rel in sorted(files):
        print_change(f"{label}{rel}")
        show_diff(read(dst / rel), "", labels.current, labels.target)
    if not files:
        print_change(label, f"{labels.current} exists, {labels.target} is absent")


def _show_tree_file_diffs(label: str, src: Path, dst: Path, labels: DiffLabels) -> bool:
    showed = False
    current_files = rel_files(dst)
    target_files = rel_files(src)
    for rel in sorted(current_files | target_files):
        current = read(dst / rel) if rel in current_files else None
        target = read(src / rel) if rel in target_files else ""
        if current != target:
            showed = True
            print_change(f"{label}{rel}")
            show_diff(current, target, labels.current, labels.target)
    return showed
