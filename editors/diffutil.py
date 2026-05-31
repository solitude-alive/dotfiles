"""Text diff helpers shared by check and apply."""

import difflib
import sys


def show_diff(current: str | None, target: str) -> None:
    diff = difflib.unified_diff(
        (current or "").splitlines(True), target.splitlines(True), "live", "repo"
    )
    sys.stdout.writelines("      " + line for line in diff)


def compare(label: str, repo: str | None, live: str | None) -> bool:
    """True if drift; prints status (and diff on mismatch)."""
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
