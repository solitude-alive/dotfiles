"""Filesystem primitives used by sync operations."""

import shutil
from pathlib import Path

from .types import BeforeChange


def rel_files(root: Path) -> set[Path]:
    if not root.is_dir():
        return set()
    return {path.relative_to(root) for path in root.rglob("*") if path.is_file()}


def rel_entries(root: Path) -> set[Path]:
    if not root.is_dir():
        return set()
    return {path.relative_to(root) for path in root.rglob("*")}


def has_tree(root: Path) -> bool:
    return root.is_dir() and any(root.iterdir())


def tree_absent_or_empty(root: Path) -> bool:
    return not root.exists() or (root.is_dir() and not any(root.iterdir()))


def write_text(path: Path, text: str, before_change: BeforeChange | None) -> None:
    run_before_change(path, before_change)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def remove_path(path: Path, before_change: BeforeChange | None) -> None:
    run_before_change(path, before_change)
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def replace_tree(src: Path, dst: Path, before_change: BeforeChange | None) -> None:
    remove_path(dst, before_change)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst)


def run_before_change(path: Path, callback: BeforeChange | None) -> None:
    if callback:
        callback(path)
