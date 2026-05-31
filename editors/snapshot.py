"""snapshot: live config -> repo.   check: report drift (no writes)."""

import shutil

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
from diffutil import compare


def snapshot() -> int:
    for name, (support, extdir, _cli) in EDITORS.items():
        src, dst = user_dir(support), REPO / name
        if not src.is_dir():
            print(f"  [{name}] not installed, skipping")
            continue
        dst.mkdir(parents=True, exist_ok=True)
        print(f"  [{name}] {src}")

        if (src / "settings.json").is_file():
            (dst / "settings.json").write_text(redacted_settings(src / "settings.json"))
            print("    + settings.json")
        for fname in COPY_FILES:
            if (src / fname).is_file():
                (dst / fname).write_text(read_copy(src / fname))
                print(f"    + {fname}")

        snip = src / "snippets"
        if snip.is_dir() and any(snip.iterdir()):
            shutil.rmtree(dst / "snippets", ignore_errors=True)
            shutil.copytree(snip, dst / "snippets")
            print("    + snippets/")

        exts = live_extensions(extdir)
        if exts is not None:
            (dst / "extensions.txt").write_text(exts)
            print(f"    + extensions.txt ({exts.count(chr(10))} ids)")
    print("Done. Review with: git diff editors/")
    return 0


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
        drift |= compare(
            "extensions.txt", read(REPO / name / "extensions.txt"), live_extensions(extdir)
        )
    print()
    if drift:
        print("Drift detected. Run ./editors.sh snapshot to refresh.")
        return 1
    print("No drift: snapshot matches live config.")
    return 0
