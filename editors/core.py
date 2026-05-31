"""Shared helpers for the editor snapshot tool (no flow, just utilities)."""

import json
import shutil
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent
HOME = Path.home()

# Machine-local keys: redacted on snapshot, preserved on apply.
IGNORE = {"remote.SSH.remotePlatform"}

# name -> (support dir under config base, extensions dir under HOME, CLI name)
EDITORS = {
    "vscode": ("Code", ".vscode", "code"),
    "cursor": ("Cursor", ".cursor", "cursor"),
}
COPY_FILES = ("keybindings.json", "tasks.json")


def user_dir(support: str) -> Path:
    if sys.platform == "darwin":
        base = HOME / "Library" / "Application Support"
    elif sys.platform.startswith("linux"):
        base = HOME / ".config"
    else:
        sys.exit(f"unsupported os: {sys.platform}")
    return base / support / "User"


def load_json(path: Path):
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def read(path: Path) -> str | None:
    return path.read_text() if path.is_file() else None


def read_copy(path: Path) -> str | None:
    """Verbatim file text, normalized to end with exactly one newline."""
    text = read(path)
    if not text:
        return text
    return text if text.endswith("\n") else text + "\n"


def dump_settings(data: dict) -> str:
    return json.dumps(data, indent=4, ensure_ascii=False) + "\n"


def redacted_settings(path: Path) -> str | None:
    """Live settings as text, with IGNORE keys stripped (what the repo stores)."""
    data = load_json(path)
    if data is None:
        return None
    for key in IGNORE:
        data.pop(key, None)
    return dump_settings(data)


def live_extensions(extdir: str) -> str | None:
    data = load_json(HOME / extdir / "extensions" / "extensions.json")
    if data is None:
        return None
    return "\n".join(sorted({e["identifier"]["id"] for e in data})) + "\n"


def backup(path: Path) -> None:
    if path.exists():
        bak = path.with_name(f"{path.name}.backup.{int(time.time())}")
        shutil.copy2(path, bak)
        print(f"      backed up -> {bak.name}")
