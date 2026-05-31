"""Diff display helpers."""

import difflib
import sys

from .types import DiffLabels


def show_diff(
    current: str | None,
    target: str,
    current_label: str = "live",
    target_label: str = "repo",
) -> None:
    labels = DiffLabels(current_label, target_label)
    diff = difflib.unified_diff(
        (current or "").splitlines(True),
        target.splitlines(True),
        labels.current,
        labels.target,
    )
    for line in diff:
        sys.stdout.write("      " + line)
        if not line.endswith("\n"):
            sys.stdout.write("\n")


def print_change(label: str, detail: str | None = None) -> None:
    suffix = f": {detail}" if detail else ":"
    print(f"    CHANGE {label}{suffix}")
