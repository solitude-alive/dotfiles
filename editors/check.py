"""check: report drift between repo snapshot and live editor config."""

from pathlib import Path

from core import (
    COPY_FILES,
    EDITORS,
    REPO,
    live_extensions,
    read,
    read_copy,
    redacted_settings,
    user_dir,
)
from sync import rel_entries, rel_files, show_diff


def compare(label: str, repo: str | None, live: str | None) -> bool:
    """True if drift; prints status and diff on mismatch."""
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


def compare_tree(label: str, repo_dir: Path, live_dir: Path) -> bool:
    """True if tree drift; prints status and per-file diffs."""
    repo_entries = rel_entries(repo_dir)
    live_entries = rel_entries(live_dir)
    if not repo_entries and not live_entries:
        return False

    drift = repo_entries != live_entries
    showed_file_diff = False
    for rel in sorted(rel_files(repo_dir) | rel_files(live_dir)):
        repo = read(repo_dir / rel) if (repo_dir / rel).is_file() else None
        live = read(live_dir / rel) if (live_dir / rel).is_file() else None
        if repo != live:
            drift = True
            showed_file_diff = True
            print(f"    DRIFT {label}{rel}:")
            show_diff(live, repo)

    if drift and not showed_file_diff:
        print(f"    DRIFT {label}: directory entries differ")
    elif not drift:
        print(f"    ok    {label}")
    return drift


def check() -> int:
    drift = False
    for name, (support, extdir, _cli) in EDITORS.items():
        src = user_dir(support)
        print(f"== {name} ==")
        if not src.is_dir():
            print("    (not installed, skipping)")
            continue
        live_s = (
            redacted_settings(src / "settings.json") if (src / "settings.json").is_file() else None
        )
        drift |= compare("settings.json", read(REPO / name / "settings.json"), live_s)
        for fname in COPY_FILES:
            drift |= compare(fname, read(REPO / name / fname), read_copy(src / fname))
        drift |= compare_tree("snippets/", REPO / name / "snippets", src / "snippets")
        drift |= compare(
            "extensions.txt",
            read(REPO / name / "extensions.txt"),
            live_extensions(extdir),
        )
    print()
    if drift:
        print("Drift detected. Run ./editors.sh snapshot to refresh.")
        return 1
    print("No drift: snapshot matches live config.")
    return 0
