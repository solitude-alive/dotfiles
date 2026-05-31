"""Whole text-file sync."""

import argparse
from pathlib import Path

from core import read

from .diff import print_change, show_diff
from .paths import remove_path, write_text
from .prompt import approve
from .types import BeforeChange, DiffLabels, SyncResult


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
) -> SyncResult:
    """Sync one text file."""
    labels = DiffLabels(current_label, target_label)
    current = read(dst)

    if target is None:
        if current is None:
            return SyncResult()
        print_change(label)
        show_diff(current, "", labels.current, labels.target)
        if approve(remove_desc or f"remove {label}", args):
            remove_path(dst, before_change)
            return SyncResult(changed=True, wrote=True)
        return SyncResult(changed=True)

    if current == target:
        return SyncResult()

    print_change(label)
    show_diff(current, target, labels.current, labels.target)
    if approve(write_desc or f"write {label}", args):
        write_text(dst, target, before_change)
        return SyncResult(changed=True, wrote=True)
    return SyncResult(changed=True)
