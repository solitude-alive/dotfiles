#!/usr/bin/env python3
"""Editor config tool: snapshot | check | apply. See README.md."""

import argparse
import sys

import apply as apply_mod
import snapshot as snap


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sp = sub.add_parser("snapshot", help="capture live config into the repo")
    sp.add_argument(
        "editor", nargs="?", choices=list(apply_mod.EDITORS), help="limit to one editor"
    )
    sp.add_argument("--dry-run", action="store_true", help="show changes, write nothing")
    sp.add_argument("--force", action="store_true", help="no prompts; snapshot everything")
    sub.add_parser("check", help="report drift between repo and live")
    ap = sub.add_parser("apply", help="apply repo onto this machine (clean mirror)")
    ap.add_argument(
        "editor", nargs="?", choices=list(apply_mod.EDITORS), help="limit to one editor"
    )
    ap.add_argument("--dry-run", action="store_true", help="show changes, write nothing")
    ap.add_argument("--force", action="store_true", help="no prompts; apply everything")
    args = parser.parse_args()

    if args.cmd == "snapshot":
        return snap.snapshot(args)
    if args.cmd == "check":
        return snap.check()
    return apply_mod.apply(args)


if __name__ == "__main__":
    sys.exit(main())
