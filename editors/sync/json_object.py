"""Top-level-key sync for JSON object files."""

import argparse
import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from core import dump_settings, load_json

from .diff import print_change
from .paths import write_text
from .prompt import approve
from .text import sync_text
from .types import BeforeChange, JsonDelta, JsonObject, SyncResult


def sync_json_object(
    label: str,
    dst: Path,
    target: JsonObject,
    args: argparse.Namespace,
    *,
    current_label: str,
    target_label: str,
    before_change: BeforeChange | None = None,
) -> SyncResult:
    """Sync one JSON object file by top-level key."""
    current = _load_json_object(dst)
    if current is None:
        return sync_text(
            label,
            dst,
            dump_settings(target),
            args,
            current_label=current_label,
            target_label=target_label,
            before_change=before_change,
        )

    deltas = list(_json_deltas(current, target))
    if not deltas:
        return SyncResult()

    print_change(label)
    next_data = dict(current)
    wrote = False

    for delta in deltas:
        _print_delta(delta)
        if approve(_action_desc(label, delta), args):
            _apply_delta(next_data, delta)
            wrote = True

    if wrote:
        text = dump_settings(target if args.force else next_data)
        write_text(dst, text, before_change)
    return SyncResult(changed=True, wrote=wrote)


def _json_value(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _load_json_object(path: Path) -> JsonObject | None:
    if not path.exists():
        return {}
    data = load_json(path)
    return data if isinstance(data, dict) else None


def _json_deltas(current: JsonObject, target: JsonObject) -> Iterable[JsonDelta]:
    keys = list(current)
    keys.extend(key for key in target if key not in current)

    for key in keys:
        has_current = key in current
        has_target = key in target
        if has_current and has_target and current[key] == target[key]:
            continue
        if has_current and not has_target:
            yield JsonDelta("remove", key, current=current[key])
        elif has_target and not has_current:
            yield JsonDelta("add", key, target=target[key])
        else:
            yield JsonDelta("update", key, current=current[key], target=target[key])


def _print_delta(delta: JsonDelta) -> None:
    if delta.kind == "remove":
        print(f"      - {delta.key}: {_json_value(delta.current)}")
    elif delta.kind == "add":
        print(f"      + {delta.key}: {_json_value(delta.target)}")
    else:
        print(f"      ~ {delta.key}:")
        print(f"        - {_json_value(delta.current)}")
        print(f"        + {_json_value(delta.target)}")


def _action_desc(label: str, delta: JsonDelta) -> str:
    if delta.kind == "remove":
        return f"remove {label} key {delta.key}"
    if delta.kind == "add":
        return f"add {label} key {delta.key}"
    return f"update {label} key {delta.key}"


def _apply_delta(data: JsonObject, delta: JsonDelta) -> None:
    if delta.kind == "remove":
        data.pop(delta.key, None)
    else:
        data[delta.key] = delta.target
