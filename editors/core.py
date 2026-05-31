"""Shared helpers for the editor snapshot tool (no flow, just utilities)."""

import json
import shutil
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent
HOME = Path.home()


def load_json_file(path: Path):
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def load_ignore() -> tuple[set[str], set[str]]:
    data = load_json_file(REPO / "ignore.json") or {}
    if not isinstance(data, dict):
        return set(), set()
    return set(data.get("settings", [])), set(data.get("extensions", []))


SETTINGS_IGNORE, EXTENSIONS_IGNORE = load_ignore()

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
    return load_json_file(path)


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


def redacted_settings_data(path: Path) -> dict | None:
    """Settings data with ignored keys stripped (what the repo stores)."""
    data = load_json(path)
    if not isinstance(data, dict):
        return None
    return tracked_settings_data(data)


def tracked_settings_data(data: dict) -> dict:
    """Copy settings data without ignored keys."""
    return {key: value for key, value in data.items() if key not in SETTINGS_IGNORE}


def redacted_settings(path: Path) -> str | None:
    """Live settings as text, with ignored keys stripped (what the repo stores)."""
    data = redacted_settings_data(path)
    return dump_settings(data) if data is not None else None


def live_extensions(extdir: str) -> str | None:
    data = load_json(HOME / extdir / "extensions" / "extensions.json")
    if data is None:
        return None
    return format_extensions({e["identifier"]["id"] for e in data})


def read_extensions(path: Path) -> str | None:
    text = read(path)
    if text is None:
        return None
    return format_extensions({x.strip() for x in text.splitlines() if x.strip()})


def format_extensions(ids: set[str]) -> str:
    return "\n".join(sorted(ids - EXTENSIONS_IGNORE)) + "\n"


def backup(path: Path) -> None:
    if path.exists():
        stamp = int(time.time())
        bak = path.with_name(f"{path.name}.backup.{stamp}")
        n = 1
        while bak.exists():
            bak = path.with_name(f"{path.name}.backup.{stamp}.{n}")
            n += 1
        if path.is_dir():
            shutil.copytree(path, bak)
        else:
            shutil.copy2(path, bak)
        print(f"      backed up -> {bak.name}")
