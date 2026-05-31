"""Small types shared by sync modules."""

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

BeforeChange = Callable[[Path], None]
JsonObject = dict[str, Any]
DeltaKind = Literal["add", "remove", "update"]


@dataclass(frozen=True)
class SyncResult:
    changed: bool = False
    wrote: bool = False


@dataclass(frozen=True)
class DiffLabels:
    current: str
    target: str


@dataclass(frozen=True)
class JsonDelta:
    kind: DeltaKind
    key: str
    current: Any = None
    target: Any = None


@dataclass(frozen=True)
class LineDelta:
    kind: Literal["add", "remove"]
    value: str
