"""SQLite storage layer: schema, migrations and repositories for lablog.

The database lives in ``<project>/.lablog/lablog.db`` and holds runs, their
parameters/metrics, step-indexed series, tags and artifacts.  All access goes
through :class:`Storage`, which owns a single connection configured with WAL
journaling and foreign keys enabled.
"""

from __future__ import annotations

import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple, Union

from .models import (
    RUN_STATUSES,
    Artifact,
    Run,
    coerce_mapping,
    new_run_id,
    utc_now_iso,
)

__all__ = [
    "Storage",
    "RunNotFound",
    "find_project_root",
    "default_db_path",
    "STATE_DIR",
    "DB_FILENAME",
]

STATE_DIR = ".lablog"
DB_FILENAME = "lablog.db"
SCHEMA_VERSION = 1

_METRIC_OPS = (">=", "<=", "!=", "==", ">", "<")

SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS runs (
    id          TEXT PRIMARY KEY,
    experiment  TEXT NOT NULL,
    name        TEXT,
    status      TEXT NOT NULL DEFAULT 'running',
    started_at  TEXT NOT NULL,
    finished_at TEXT,
    host        TEXT,
    git_commit  TEXT,
    notes       TEXT
);
CREATE INDEX IF NOT EXISTS idx_runs_experiment ON runs(experiment);
CREATE INDEX IF NOT EXISTS idx_runs_status ON runs(status);
CREATE INDEX IF NOT EXISTS idx_runs_started ON runs(started_at);

CREATE TABLE IF NOT EXISTS entries (
    run_id     TEXT NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    kind       TEXT NOT NULL CHECK (kind IN ('param', 'metric')),
    key        TEXT NOT NULL,
    value_type TEXT NOT NULL,
    value_num  REAL,
    value_text TEXT,
    PRIMARY KEY (run_id, kind, key)
);
CREATE INDEX IF NOT EXISTS idx_entries_lookup ON entries(kind, key);

CREATE TABLE IF NOT EXISTS series (
    run_id TEXT NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    name   TEXT NOT NULL,
    step   REAL NOT NULL,
    value  REAL NOT NULL,
    PRIMARY KEY (run_id, name, step)
);
CREATE INDEX IF NOT EXISTS idx_series_name ON series(name);

CREATE TABLE IF NOT EXISTS tags (
    run_id TEXT NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    tag    TEXT NOT NULL,
    PRIMARY KEY (run_id, tag)
);

CREATE TABLE IF NOT EXISTS artifacts (
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    name   TEXT NOT NULL,
    uri    TEXT NOT NULL,
    size   INTEGER,
    sha256 TEXT
);
CREATE INDEX IF NOT EXISTS idx_artifacts_run ON artifacts(run_id);
"""


class RunNotFound(KeyError):
    """Raised when a run id (or unambiguous prefix) cannot be resolved."""

    def __init__(self, run_id: str, candidates: Optional[Sequence[str]] = None):
        self.run_id = run_id
        self.candidates = list(candidates or [])
        if self.candidates:
            detail = f"ambiguous run prefix {run_id!r}; matches: {', '.join(self.candidates)}"
        else:
            detail = f"no run matches {run_id!r}"
        super().__init__(detail)


def find_project_root(start: Union[str, Path] = ".") -> Path:
    """Walk upwards looking for a ``.lablog`` directory or ``experiments.toml``."""
    current = Path(start).resolve()
    if current.is_file():
        current = current.parent
    for candidate in [current, *current.parents]:
        if (candidate / STATE_DIR).is_dir() or (candidate / "experiments.toml").is_file():
            return candidate
    return current


def default_db_path(root: Union[str, Path]) -> Path:
    return Path(root) / STATE_DIR / DB_FILENAME


Value = Union[int, float, bool, str]


def _value_columns(value: Any) -> Tuple[str, Optional[float], Optional[str]]:
    if isinstance(value, bool):
        return "bool", float(int(value)), "true" if value else "false"
    if isinstance(value, int):
        return "int", float(value), str(value)
    if isinstance(value, float):
        return "float", float(value), repr(value)
    if value is None:
        return "str", None, ""
    return "str", None, str(value)


def _decode_value(value_type: str, value_num: Optional[float], value_text: Optional[str]) -> Any:
    if value_type == "bool":
        return bool(value_num)
    if value_type == "int":
        return int(value_num) if value_num is not None else 0
    if value_type == "float":
        return float(value_num) if value_num is not None else 0.0
    return value_text if value_text is not None else ""


@dataclass
class _FilterClause:
    sql: str
    params: List[Any]


class Storage:
    """A thin, explicit repository over the lablog SQLite database.

    Instances are usable as context managers::

        with Storage("proj/.lablog/lablog.db") as store:
            run = store.create_run("demo", params={"lr": 0.1})
    """

    def __init__(self, path: Union[str, Path], *, create: bool = True):
        self.path = Path(path)
        if create:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        elif not self.path.exists():
            raise FileNotFoundError(f"database not found: {self.path}")
        self.conn = sqlite3.connect(str(self.path), isolation_level=None)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")
        self.conn.execute("PRAGMA synchronous=NORMAL")
        if create:
            self._init_schema()

    # ------------------------------------------------------------------ plumbing
    def __enter__(self) -> "Storage":
        return self

    def __exit__(self, *exc_info: Any) -> None:
        self.close()

    def close(self) -> None:
        try:
            self.conn.close()
        except sqlite3.Error:  # pragma: no cover - defensive
            pass

    def _init_schema(self) -> None:
        self.conn.executescript(SCHEMA)
        row = self.conn.execute("SELECT value FROM meta WHERE key = 'schema_version'").fetchone()
        if row is None:
            self.conn.execute(
                "INSERT INTO meta(key, value) VALUES('schema_version', ?)",
                (str(SCHEMA_VERSION),),
            )
            self.conn.execute(
                "INSERT INTO meta(key, value) VALUES('created_at', ?)", (utc_now_iso(),)
            )
        elif int(row["value"]) != SCHEMA_VERSION:
            raise RuntimeError(
                f"database schema v{row['value']} is not supported by this build "
                f"(expected v{SCHEMA_VERSION})"
            )

    def schema_version(self) -> int:
        row = self.conn.execute("SELECT value FROM meta WHERE key = 'schema_version'").fetchone()
        return int(row["value"]) if row else 0

    # ------------------------------------------------------------------ writes
    def create_run(
        self,
        experiment: str,
        *,
        name: Optional[str] = None,
        run_id: Optional[str] = None,
        params: Optional[Mapping[str, Any]] = None,
        tags: Optional[Iterable[str]] = None,
        host: Optional[str] = None,
        git_commit: Optional[str] = None,
        notes: Optional[str] = None,
        status: str = "running",
        started_at: Optional[str] = None,
    ) -> Run:
        if status not in RUN_STATUSES:
            raise ValueError(f"invalid status {status!r}; expected one of {RUN_STATUSES}")
        rid = run_id or new_run_id()
        started = started_at or utc_now_iso()
        with self.conn:
            self.conn.execute(
                "INSERT INTO runs(id, experiment, name, status, started_at, host, git_commit,"
                " notes) VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
                (rid, experiment, name, status, started, host, git_commit, notes),
            )
        if params:
            self.log_params(rid, params)
        if tags:
            self.add_tags(rid, tags)
        return self.get_run(rid)

    def update_run(self, run_id: str, **fields: Any) -> Run:
        """Update scalar fields (``name``, ``status``, ``notes``, ...)."""
        allowed = {"name", "status", "notes", "host", "git_commit", "finished_at", "experiment"}
        unknown = set(fields) - allowed
        if unknown:
            raise ValueError(f"cannot update unknown field(s): {', '.join(sorted(unknown))}")
        if "status" in fields and fields["status"] not in RUN_STATUSES:
            raise ValueError(f"invalid status {fields['status']!r}")
        resolved = self.resolve_id(run_id)
        if not fields:
            return self.get_run(resolved)
        assignments = ", ".join(f"{key} = ?" for key in fields)
        values = [fields[key] for key in fields]
        with self.conn:
            self.conn.execute(
                f"UPDATE runs SET {assignments} WHERE id = ?", (*values, resolved)
            )
        return self.get_run(resolved)

    def finish_run(self, run_id: str, *, status: str = "finished", notes: Optional[str] = None) -> Run:
        if status not in ("finished", "failed", "aborted"):
            raise ValueError("finish_run status must be finished, failed or aborted")
        fields: Dict[str, Any] = {"status": status, "finished_at": utc_now_iso()}
        if notes is not None:
            fields["notes"] = notes
        return self.update_run(run_id, **fields)

    def log_params(self, run_id: str, params: Mapping[str, Any] | Iterable[str]) -> Dict[str, Any]:
        return self._log_entries(run_id, "param", params)

    def log_metrics(self, run_id: str, metrics: Mapping[str, Any] | Iterable[str]) -> Dict[str, Any]:
        return self._log_entries(run_id, "metric", metrics)

    def _log_entries(
        self, run_id: str, kind: str, values: Mapping[str, Any] | Iterable[str]
    ) -> Dict[str, Any]:
        resolved = self.resolve_id(run_id)
        mapping = coerce_mapping(values) if not isinstance(values, Mapping) else dict(values)
        with self.conn:
            for key, raw in mapping.items():
                value_type, num, text = _value_columns(raw)
                self.conn.execute(
                    "INSERT INTO entries(run_id, kind, key, value_type, value_num, value_text)"
                    " VALUES(?, ?, ?, ?, ?, ?)"
                    " ON CONFLICT(run_id, kind, key) DO UPDATE SET"
                    " value_type = excluded.value_type,"
                    " value_num = excluded.value_num,"
                    " value_text = excluded.value_text",
                    (resolved, kind, str(key), value_type, num, text),
                )
        return mapping

    def log_series(self, run_id: str, name: str, points: Iterable[Sequence[float]]) -> int:
        resolved = self.resolve_id(run_id)
        rows = [(resolved, str(name), float(step), float(value)) for step, value in points]
        with self.conn:
            self.conn.executemany(
                "INSERT INTO series(run_id, name, step, value) VALUES(?, ?, ?, ?)"
                " ON CONFLICT(run_id, name, step) DO UPDATE SET value = excluded.value",
                rows,
            )
        return len(rows)

    def add_tags(self, run_id: str, tags: Iterable[str]) -> List[str]:
        resolved = self.resolve_id(run_id)
        cleaned = [str(tag) for tag in tags if str(tag)]
        with self.conn:
            self.conn.executemany(
                "INSERT OR IGNORE INTO tags(run_id, tag) VALUES(?, ?)",
                [(resolved, tag) for tag in cleaned],
            )
        return self.tags(resolved)

    def remove_tag(self, run_id: str, tag: str) -> bool:
        resolved = self.resolve_id(run_id)
        with self.conn:
            cursor = self.conn.execute(
                "DELETE FROM tags WHERE run_id = ? AND tag = ?", (resolved, tag)
            )
        return cursor.rowcount > 0

    def add_artifact(
        self,
        run_id: str,
        name: str,
        uri: str,
        *,
        size: Optional[int] = None,
        sha256: Optional[str] = None,
    ) -> Artifact:
        resolved = self.resolve_id(run_id)
        with self.conn:
            self.conn.execute(
                "INSERT INTO artifacts(run_id, name, uri, size, sha256) VALUES(?, ?, ?, ?, ?)",
                (resolved, name, uri, size, sha256),
            )
        return Artifact(name=name, uri=uri, size=size, sha256=sha256)

    def delete_run(self, run_id: str) -> bool:
        resolved = self.resolve_id(run_id)
        with self.conn:
            cursor = self.conn.execute("DELETE FROM runs WHERE id = ?", (resolved,))
        return cursor.rowcount > 0

    # ------------------------------------------------------------------ reads
    def resolve_id(self, run_id_or_prefix: str) -> str:
        """Resolve a full id or a unique prefix, raising :class:`RunNotFound`."""
        exact = self.conn.execute("SELECT id FROM runs WHERE id = ?", (run_id_or_prefix,)).fetchone()
        if exact:
            return exact["id"]
        matches = [
            row["id"]
            for row in self.conn.execute(
                "SELECT id FROM runs WHERE id LIKE ? ORDER BY id LIMIT 25",
                (f"{run_id_or_prefix}%",),
            )
        ]
        if len(matches) == 1:
            return matches[0]
        raise RunNotFound(run_id_or_prefix, matches)

    def tags(self, run_id: str) -> List[str]:
        resolved = self.resolve_id(run_id)
        return [
            row["tag"]
            for row in self.conn.execute(
                "SELECT tag FROM tags WHERE run_id = ? ORDER BY tag", (resolved,)
            )
        ]

    def series(self, run_id: str, name: Optional[str] = None) -> Dict[str, List[List[float]]]:
        resolved = self.resolve_id(run_id)
        sql = "SELECT name, step, value FROM series WHERE run_id = ?"
        args: List[Any] = [resolved]
        if name:
            sql += " AND name = ?"
            args.append(name)
        sql += " ORDER BY name, step"
        out: Dict[str, List[List[float]]] = {}
        for row in self.conn.execute(sql, args):
            out.setdefault(row["name"], []).append([row["step"], row["value"]])
        return out

    def get_run(self, run_id: str, *, include_series: bool = True) -> Run:
        resolved = self.resolve_id(run_id)
        row = self.conn.execute("SELECT * FROM runs WHERE id = ?", (resolved,)).fetchone()
        if row is None:  # pragma: no cover - resolve_id guarantees existence
            raise RunNotFound(run_id)
        run = Run(
            id=row["id"],
            experiment=row["experiment"],
            status=row["status"],
            name=row["name"],
            started_at=row["started_at"],
            finished_at=row["finished_at"],
            host=row["host"],
            git_commit=row["git_commit"],
            notes=row["notes"],
        )
        for entry in self.conn.execute(
            "SELECT kind, key, value_type, value_num, value_text FROM entries WHERE run_id = ?",
            (resolved,),
        ):
            value = _decode_value(entry["value_type"], entry["value_num"], entry["value_text"])
            if entry["kind"] == "param":
                run.params[entry["key"]] = value
            else:
                run.metrics[entry["key"]] = value
        run.tags = self.tags(resolved)
        run.artifacts = [
            Artifact(name=r["name"], uri=r["uri"], size=r["size"], sha256=r["sha256"])
            for r in self.conn.execute(
                "SELECT name, uri, size, sha256 FROM artifacts WHERE run_id = ? ORDER BY id",
                (resolved,),
            )
        ]
        if include_series:
            run.series = self.series(resolved)
        return run

    def count_runs(self) -> int:
        return int(self.conn.execute("SELECT COUNT(*) AS c FROM runs").fetchone()["c"])

    def experiments(self) -> List[Dict[str, Any]]:
        """One summary row per experiment name."""
        rows = self.conn.execute(
            """
            SELECT experiment,
                   COUNT(*) AS runs,
                   SUM(CASE WHEN status = 'finished' THEN 1 ELSE 0 END) AS finished,
                   SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS failed,
                   MAX(started_at) AS last_started
            FROM runs
            GROUP BY experiment
            ORDER BY experiment
            """
        ).fetchall()
        return [
            {
                "experiment": r["experiment"],
                "runs": r["runs"],
                "finished": r["finished"] or 0,
                "failed": r["failed"] or 0,
                "last_started": r["last_started"],
            }
            for r in rows
        ]

    def overview(self) -> Dict[str, Any]:
        row = self.conn.execute(
            """
            SELECT COUNT(*) AS runs,
                   SUM(CASE WHEN status = 'running' THEN 1 ELSE 0 END) AS running,
                   SUM(CASE WHEN status = 'finished' THEN 1 ELSE 0 END) AS finished,
                   SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS failed
            FROM runs
            """
        ).fetchone()
        metric_keys = [
            r["key"]
            for r in self.conn.execute(
                "SELECT DISTINCT key FROM entries WHERE kind = 'metric' ORDER BY key LIMIT 20"
            )
        ]
        return {
            "runs": row["runs"] or 0,
            "running": row["running"] or 0,
            "finished": row["finished"] or 0,
            "failed": row["failed"] or 0,
            "experiments": len(self.experiments()),
            "metrics": metric_keys,
            "schema_version": self.schema_version(),
        }

    def _build_filters(
        self,
        *,
        experiment: Optional[str],
        status: Optional[Union[str, Sequence[str]]],
        tag: Optional[str],
        name_contains: Optional[str],
        params: Optional[Mapping[str, Any]],
        metrics: Optional[Mapping[str, Tuple[str, Any]]],
        since: Optional[str],
    ) -> _FilterClause:
        clauses: List[str] = []
        args: List[Any] = []

        if experiment:
            clauses.append("runs.experiment = ?")
            args.append(experiment)
        if status:
            statuses = [status] if isinstance(status, str) else list(status)
            placeholders = ", ".join("?" for _ in statuses)
            clauses.append(f"runs.status IN ({placeholders})")
            args.extend(statuses)
        if tag:
            clauses.append("EXISTS (SELECT 1 FROM tags t WHERE t.run_id = runs.id AND t.tag = ?)")
            args.append(tag)
        if name_contains:
            clauses.append("COALESCE(runs.name, '') LIKE ?")
            args.append(f"%{name_contains}%")
        if since:
            clauses.append("runs.started_at >= ?")
            args.append(since)

        for key, expected in (params or {}).items():
            num, text, numeric = _filter_query_values(expected)
            if numeric:
                clauses.append(
                    "EXISTS (SELECT 1 FROM entries e WHERE e.run_id = runs.id"
                    " AND e.kind = 'param' AND e.key = ? AND e.value_num = ?)"
                )
                args.extend([key, num])
            else:
                clauses.append(
                    "EXISTS (SELECT 1 FROM entries e WHERE e.run_id = runs.id"
                    " AND e.kind = 'param' AND e.key = ? AND e.value_text = ?)"
                )
                args.extend([key, text])

        for key, (op, expected) in (metrics or {}).items():
            if op not in _METRIC_OPS:
                raise ValueError(f"invalid metric operator {op!r}; use one of {_METRIC_OPS}")
            num, text, numeric = _filter_query_values(expected)
            column = "e.value_num" if numeric else "e.value_text"
            value = num if numeric else text
            clauses.append(
                "EXISTS (SELECT 1 FROM entries e WHERE e.run_id = runs.id"
                f" AND e.kind = 'metric' AND e.key = ? AND {column} {op} ?)"
            )
            args.extend([key, value])

        sql = " AND ".join(clauses)
        return _FilterClause(sql=sql, params=args)

    def list_runs(
        self,
        *,
        experiment: Optional[str] = None,
        status: Optional[Union[str, Sequence[str]]] = None,
        tag: Optional[str] = None,
        name_contains: Optional[str] = None,
        params: Optional[Mapping[str, Any]] = None,
        metrics: Optional[Mapping[str, Tuple[str, Any]]] = None,
        since: Optional[str] = None,
        order_by: str = "started_at",
        descending: bool = True,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> List[Run]:
        order_column = {
            "started_at": "runs.started_at",
            "id": "runs.id",
            "experiment": "runs.experiment",
            "name": "COALESCE(runs.name, '')",
            "status": "runs.status",
        }.get(order_by)
        if order_column is None:
            raise ValueError(f"unsupported order_by {order_by!r}")

        filters = self._build_filters(
            experiment=experiment,
            status=status,
            tag=tag,
            name_contains=name_contains,
            params=params,
            metrics=metrics,
            since=since,
        )
        sql = "SELECT runs.id FROM runs"
        if filters.sql:
            sql += f" WHERE {filters.sql}"
        sql += f" ORDER BY {order_column} {'DESC' if descending else 'ASC'}, runs.id"
        args = list(filters.params)
        if limit is not None:
            sql += " LIMIT ?"
            args.append(int(limit))
            if offset:
                sql += " OFFSET ?"
                args.append(int(offset))
        elif offset:
            sql += " LIMIT -1 OFFSET ?"
            args.append(int(offset))

        ids = [row["id"] for row in self.conn.execute(sql, args)]
        return [self.get_run(rid, include_series=False) for rid in ids]


def _filter_query_values(expected: Any) -> Tuple[Optional[float], Optional[str], bool]:
    if isinstance(expected, bool):
        return None, "true" if expected else "false", False
    if isinstance(expected, (int, float)):
        return float(expected), None, True
    return None, str(expected), False
