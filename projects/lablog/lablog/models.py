"""Domain models and small value helpers."""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, Optional

__all__ = [
    "Run",
    "Artifact",
    "RUN_STATUSES",
    "new_run_id",
    "utc_now_iso",
    "coerce_value",
    "format_value",
]

RUN_STATUSES = ("running", "finished", "failed", "aborted")

_TRUE = {"1", "true", "yes", "y", "on"}
_FALSE = {"0", "false", "no", "n", "off"}


def utc_now_iso() -> str:
    """Current UTC timestamp in a lexicographically sortable ISO-8601 form."""
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def new_run_id() -> str:
    """Sortable run identifier: millisecond timestamp + random suffix.

    Sorting run ids lexicographically therefore mostly sorts them by creation
    time, which keeps listings stable without relying on a separate index.
    """
    return f"r{int(time.time() * 1000):013x}{secrets.token_hex(3)}"


def coerce_value(raw: str) -> Any:
    """Convert a CLI/config string into ``bool``, ``int``, ``float`` or ``str``.

    Deliberately conservative: ``"007"`` stays a string (leading zeros are
    meaningful for identifiers such as zip codes or model versions), and only
    unambiguous numeric forms are converted.
    """
    if not isinstance(raw, str):
        return raw
    text = raw.strip()
    lowered = text.lower()
    if lowered in _TRUE:
        return True
    if lowered in _FALSE:
        return False
    if text and (text.lstrip("+-").isdigit()):
        # avoid turning zero-padded identifiers into numbers
        if not (len(text.lstrip("+-")) > 1 and text.lstrip("+-")[0] == "0"):
            try:
                return int(text)
            except ValueError:  # pragma: no cover - defensive
                return text
    try:
        if text and any(ch in text for ch in ".eE") and text not in (".", "e", "E"):
            return float(text)
    except ValueError:  # pragma: no cover - defensive
        return text
    return text


def format_value(value: Any) -> str:
    """Render a value for text output: numeric values get light rounding."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        if value != value or value in (float("inf"), float("-inf")):
            return str(value)
        if abs(value - round(value)) < 1e-12 and abs(value) < 1e15:
            return str(int(round(value)))
        return f"{value:.6g}"
    return str(value)


@dataclass
class Artifact:
    """A file or URI attached to a run (checkpoint, plot, dataset slice...)."""

    name: str
    uri: str
    size: Optional[int] = None
    sha256: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "uri": self.uri,
            "size": self.size,
            "sha256": self.sha256,
        }


@dataclass
class Run:
    """A single experiment execution."""

    id: str
    experiment: str
    status: str = "running"
    name: Optional[str] = None
    started_at: str = field(default_factory=utc_now_iso)
    finished_at: Optional[str] = None
    host: Optional[str] = None
    git_commit: Optional[str] = None
    notes: Optional[str] = None
    params: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    artifacts: List[Artifact] = field(default_factory=list)
    series: Dict[str, List[List[float]]] = field(default_factory=dict)

    def to_dict(self, *, include_series: bool = True) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "id": self.id,
            "experiment": self.experiment,
            "status": self.status,
            "name": self.name,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "host": self.host,
            "git_commit": self.git_commit,
            "notes": self.notes,
            "params": dict(self.params),
            "metrics": dict(self.metrics),
            "tags": list(self.tags),
            "artifacts": [a.to_dict() for a in self.artifacts],
        }
        if include_series:
            payload["series"] = {k: [list(p) for p in v] for k, v in self.series.items()}
        return payload

    @property
    def display_name(self) -> str:
        return self.name or self.id


def coerce_mapping(items: Iterable[str]) -> Dict[str, Any]:
    """Parse ``["lr=0.01", "seed=3"]`` style pairs into a typed mapping."""
    result: Dict[str, Any] = {}
    for item in items or ():
        if "=" not in item:
            raise ValueError(f"expected key=value, got {item!r}")
        key, _, value = item.partition("=")
        key = key.strip()
        if not key:
            raise ValueError(f"empty key in {item!r}")
        result[key] = coerce_value(value)
    return result


def merge_mapping(base: Mapping[str, Any], extra: Mapping[str, Any]) -> Dict[str, Any]:
    merged = dict(base)
    merged.update(extra)
    return merged
