"""Export helpers: CSV, JSON and Markdown renderings of run data."""

from __future__ import annotations

import csv
import io
import json
from typing import Any, Dict, Iterable, List, Mapping, Sequence

from .models import Run, format_value

__all__ = ["flatten_run", "to_csv", "to_json", "to_markdown"]

RESERVED = {
    "id",
    "experiment",
    "name",
    "status",
    "started_at",
    "finished_at",
    "host",
    "git_commit",
    "notes",
    "tags",
}


def flatten_run(run: Run) -> Dict[str, Any]:
    """Flatten a run into a single-row mapping (params/metrics prefixed)."""
    row: Dict[str, Any] = {
        "id": run.id,
        "experiment": run.experiment,
        "name": run.name or "",
        "status": run.status,
        "started_at": run.started_at,
        "finished_at": run.finished_at or "",
        "host": run.host or "",
        "git_commit": run.git_commit or "",
        "tags": ",".join(run.tags),
    }
    for key, value in run.params.items():
        row[f"param:{key}"] = format_value(value)
    for key, value in run.metrics.items():
        row[f"metric:{key}"] = format_value(value)
    for name, points in run.series.items():
        if points:
            row[f"series:{name}:last"] = format_value(points[-1][1])
    return row


def _columns(rows: Sequence[Mapping[str, Any]]) -> List[str]:
    columns: List[str] = []
    for row in rows:
        for key in row:
            if key not in columns:
                columns.append(key)
    return columns


def to_csv(runs: Iterable[Run]) -> str:
    """Flattened CSV: one row per run, one column per param/metric."""
    rows = [flatten_run(run) for run in runs]
    buffer = io.StringIO()
    if not rows:
        return ""
    columns = _columns(rows)
    writer = csv.DictWriter(
        buffer,
        fieldnames=columns,
        extrasaction="ignore",
        # "\n" only: Python's text-mode layer adds the platform line ending, so
        # Windows gets CRLF and POSIX gets LF - without the doubled blank lines
        # that "\r\n" + text translation would produce.
        lineterminator="\n",
    )
    writer.writeheader()
    for row in rows:
        writer.writerow({key: row.get(key, "") for key in columns})
    return buffer.getvalue()


def to_json(runs: Iterable[Run]) -> str:
    return json.dumps([run.to_dict() for run in runs], indent=2, ensure_ascii=False)


def to_markdown(runs: Sequence[Run], *, metric: str | None = None) -> str:
    """A compact Markdown table for reports and README snippets."""
    if not runs:
        return "_(no runs)_\n"
    columns = ["id", "experiment", "name", "status", "started_at"]
    if metric:
        columns.append(metric)

    header = "| " + " | ".join(columns) + " |"
    divider = "| " + " | ".join("---" for _ in columns) + " |"
    lines = [header, divider]
    for run in runs:
        cells = [run.id, run.experiment, run.name or "", run.status, run.started_at]
        if metric:
            value = run.metrics.get(metric)
            cells.append("" if value is None else format_value(value))
        lines.append("| " + " | ".join(_escape(cell) for cell in cells) + " |")
    return "\n".join(lines) + "\n"


def _escape(cell: Any) -> str:
    return str(cell).replace("|", "\\|")
