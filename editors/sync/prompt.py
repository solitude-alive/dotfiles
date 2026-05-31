"""Interactive approval handling."""

import argparse


def approve(desc: str, args: argparse.Namespace) -> bool:
    if args.dry_run:
        print(f"    [dry-run] would {desc}")
        return False
    if args.force:
        print(f"    {desc}")
        return True
    return input(f"    {desc}? [y/N] ").strip().lower() in ("y", "yes")
