"""Item-by-item sync for newline-delimited sets."""

import argparse
from collections.abc import Iterable
from pathlib import Path

from core import read

from .diff import print_change
from .paths import write_text
from .prompt import approve
from .text import sync_text
from .types import BeforeChange, LineDelta, SyncResult


def sync_line_set(
    label: str,
    dst: Path,
    target_text: str | None,
    args: argparse.Namespace,
    *,
    current_label: str,
    target_label: str,
    item_name: str = "line",
    before_change: BeforeChange | None = None,
) -> SyncResult:
    """Sync a newline-delimited set one item at a time."""
    if target_text is None:
        return sync_text(
            label,
            dst,
            None,
            args,
            current_label=current_label,
            target_label=target_label,
            before_change=before_change,
        )

    current_items = _line_items(read(dst))
    target_items = _line_items(target_text)
    deltas = list(_line_deltas(current_items, target_items))
    if not deltas:
        return SyncResult()

    print_change(label)
    next_items = set(current_items)
    wrote = False

    for delta in deltas:
        _print_delta(delta)
        if approve(_action_desc(label, item_name, delta), args):
            _apply_delta(next_items, delta)
            wrote = True

    if wrote:
        text = target_text if args.force else _format_line_set(next_items)
        write_text(dst, text, before_change)
    return SyncResult(changed=True, wrote=wrote)


def _line_items(text: str | None) -> set[str]:
    return {line.strip() for line in (text or "").splitlines() if line.strip()}


def _line_deltas(current: set[str], target: set[str]) -> Iterable[LineDelta]:
    for item in sorted(current - target):
        yield LineDelta("remove", item)
    for item in sorted(target - current):
        yield LineDelta("add", item)


def _print_delta(delta: LineDelta) -> None:
    sign = "-" if delta.kind == "remove" else "+"
    print(f"      {sign} {delta.value}")


def _action_desc(label: str, item_name: str, delta: LineDelta) -> str:
    verb = "remove" if delta.kind == "remove" else "add"
    return f"{verb} {label} {item_name} {delta.value}"


def _apply_delta(items: set[str], delta: LineDelta) -> None:
    if delta.kind == "remove":
        items.discard(delta.value)
    else:
        items.add(delta.value)


def _format_line_set(items: set[str]) -> str:
    return "\n".join(sorted(items)) + "\n"
