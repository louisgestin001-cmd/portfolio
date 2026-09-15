"""Command line interface for lablog."""

from __future__ import annotations

import argparse
import json
import re
import socket
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, NoReturn, Optional, Sequence, Tuple

from . import __version__
from .compare import compare_runs
from .config import CONFIG_FILENAME, load_config
from .export import to_csv, to_json, to_markdown
from .models import RUN_STATUSES, Run, coerce_value, format_value
from .storage import STATE_DIR, Storage, default_db_path, find_project_root

__all__ = ["main", "build_parser"]

_METRIC_FILTER_RE = re.compile(r"^([A-Za-z0-9_.\-]+)\s*(>=|<=|!=|==|>|<)\s*(.+)$")

CONFIG_TEMPLATE = """# lablog project configuration
[project]
name = "{name}"
description = ""

[metrics.accuracy]
goal = "maximize"
unit = ""

[metrics.loss]
goal = "minimize"
"""


# --------------------------------------------------------------------- helpers
def _detect_git_commit() -> Optional[str]:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):  # pragma: no cover - environment dependent
        return None
    commit = result.stdout.strip()
    return commit or None


def _resolve_db(args: argparse.Namespace) -> Path:
    if getattr(args, "db", None):
        return Path(args.db)
    root = Path(args.root) if getattr(args, "root", None) else find_project_root(Path.cwd())
    return default_db_path(root)


def _open_storage(args: argparse.Namespace, *, create: bool = True) -> Storage:
    return Storage(_resolve_db(args), create=create)


def _fail(message: str) -> NoReturn:
    """Report a usage error on stderr and exit with the conventional code 2."""
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(2)


def _parse_metric_filters(items: Sequence[str]) -> Dict[str, Tuple[str, Any]]:
    filters: Dict[str, Tuple[str, Any]] = {}
    for item in items or ():
        match = _METRIC_FILTER_RE.match(item)
        if not match:
            _fail(f"--metric expects 'key>=value' style, got {item!r}")
        key, op, raw = match.groups()
        filters[key] = (op, coerce_value(raw))
    return filters


def _parse_series(items: Sequence[str]) -> Dict[str, List[List[float]]]:
    series: Dict[str, List[List[float]]] = {}
    for item in items or ():
        parts = item.split(":")
        if len(parts) != 3:
            _fail(f"--series expects name:step:value, got {item!r}")
        name, step, value = parts
        try:
            series.setdefault(name, []).append([float(step), float(value)])
        except ValueError:
            _fail(f"--series expects numeric step/value, got {item!r}")
    return series


def _parse_artifacts(items: Sequence[str]) -> List[Dict[str, Any]]:
    artifacts: List[Dict[str, Any]] = []
    for item in items or ():
        name, _, uri = item.partition("=")
        if not name or not uri:
            _fail(f"--artifact expects name=uri, got {item!r}")
        artifacts.append({"name": name, "uri": uri})
    return artifacts


def _print_table(rows: Sequence[Sequence[Any]], headers: Sequence[str]) -> None:
    str_rows = [[str(cell) for cell in row] for row in rows]
    widths = [len(h) for h in headers]
    for row in str_rows:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], len(cell))
    line = "  ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
    print(line.rstrip())
    print("  ".join("-" * widths[i] for i in range(len(headers))))
    for row in str_rows:
        print("  ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)).rstrip())


def _emit(args: argparse.Namespace, payload: Any, text: str) -> None:
    if getattr(args, "json", False):
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(text)


# ---------------------------------------------------------------------- parser
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lablog",
        description=(
            "Local-first experiment tracker: record runs, compare them with real "
            "statistics, and explore everything in a built-in dashboard."
        ),
    )
    parser.add_argument("--db", help="path to the SQLite database (default: <root>/.lablog/lablog.db)")
    parser.add_argument("--root", help="project root used to locate .lablog and experiments.toml")
    parser.add_argument("--version", action="version", version=f"lablog {__version__}")

    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="create .lablog and an experiments.toml template")
    p_init.add_argument("--name", help="project name")
    p_init.add_argument("--force", action="store_true", help="overwrite an existing experiments.toml")

    p_start = sub.add_parser("start", help="start a new run")
    p_start.add_argument("experiment")
    p_start.add_argument("--name")
    p_start.add_argument("--param", action="append", default=[], metavar="K=V")
    p_start.add_argument("--tag", action="append", default=[])
    p_start.add_argument("--notes")
    p_start.add_argument("--host")
    p_start.add_argument("--git-commit", help="commit hash, or 'auto' to read git HEAD")
    p_start.add_argument("--json", action="store_true")

    p_log = sub.add_parser("log", help="record params, metrics, series or tags on a run")
    p_log.add_argument("run")
    p_log.add_argument("--param", action="append", default=[], metavar="K=V")
    p_log.add_argument("--metric", action="append", default=[], metavar="K=V")
    p_log.add_argument("--series", action="append", default=[], metavar="NAME:STEP:VALUE")
    p_log.add_argument("--tag", action="append", default=[])
    p_log.add_argument("--artifact", action="append", default=[], metavar="NAME=URI")
    p_log.add_argument("--json", action="store_true")

    p_finish = sub.add_parser("finish", help="mark a run as finished, failed or aborted")
    p_finish.add_argument("run")
    p_finish.add_argument("--status", choices=("finished", "failed", "aborted"), default="finished")
    p_finish.add_argument("--notes")
    p_finish.add_argument("--json", action="store_true")

    p_list = sub.add_parser("list", help="list runs with optional filters")
    p_list.add_argument("--experiment")
    p_list.add_argument("--status", action="append", default=[])
    p_list.add_argument("--tag")
    p_list.add_argument("--name-contains")
    p_list.add_argument("--param", action="append", default=[], metavar="K=V")
    p_list.add_argument("--metric", action="append", default=[], metavar="KEY>=VALUE")
    p_list.add_argument("--since")
    p_list.add_argument("--order-by", default="started_at",
                        choices=("started_at", "id", "experiment", "name", "status"))
    p_list.add_argument("--asc", action="store_true")
    p_list.add_argument("--limit", type=int)
    p_list.add_argument("--offset", type=int, default=0)
    p_list.add_argument("--format", choices=("table", "json", "csv", "markdown"), default="table")
    p_list.add_argument("--json", action="store_true")

    p_show = sub.add_parser("show", help="show a run's full detail")
    p_show.add_argument("run")
    p_show.add_argument("--json", action="store_true")
    p_show.add_argument("--no-series", action="store_true")

    p_compare = sub.add_parser("compare", help="compare two or more runs")
    p_compare.add_argument("runs", nargs="+")
    p_compare.add_argument("--metric")
    p_compare.add_argument("--baseline", help="run id, id prefix, or 0-based index")
    p_compare.add_argument("--alpha", type=float, default=0.05)
    p_compare.add_argument("--json", action="store_true")

    p_export = sub.add_parser("export", help="export runs as CSV, JSON or Markdown")
    p_export.add_argument("--format", choices=("csv", "json", "markdown"), default="csv")
    p_export.add_argument("--experiment")
    p_export.add_argument("--limit", type=int)
    p_export.add_argument("--metric", help="metric column to include in the markdown table")
    p_export.add_argument("--out", help="write to a file instead of stdout")

    p_delete = sub.add_parser("delete", help="delete a run and all of its data")
    p_delete.add_argument("run")
    p_delete.add_argument("--yes", action="store_true", help="skip the confirmation prompt")

    p_stats = sub.add_parser("stats", help="show a project overview")
    p_stats.add_argument("--json", action="store_true")

    p_serve = sub.add_parser("serve", help="start the web dashboard and JSON API")
    p_serve.add_argument("--host", default="127.0.0.1")
    p_serve.add_argument("--port", type=int, default=8765)
    p_serve.add_argument("--open", action="store_true", help="print the URL prominently")

    return parser


# -------------------------------------------------------------------- handlers
def _cmd_init(args: argparse.Namespace) -> int:
    db_path = _resolve_db(args)
    root = db_path.parent.parent if db_path.parent.name == STATE_DIR else db_path.parent
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with Storage(db_path):
        pass
    config_path = root / CONFIG_FILENAME
    if config_path.exists() and not args.force:
        print(f"kept existing {config_path}")
    else:
        config_path.write_text(
            CONFIG_TEMPLATE.format(name=args.name or root.name), encoding="utf-8"
        )
        print(f"wrote {config_path}")
    print(f"initialised database at {db_path}")
    return 0


def _cmd_start(args: argparse.Namespace) -> int:
    commit = args.git_commit
    if commit == "auto":
        commit = _detect_git_commit()
    with _open_storage(args) as store:
        run = store.create_run(
            args.experiment,
            name=args.name,
            params=dict(_pairs(args.param)),
            tags=args.tag,
            host=args.host or socket.gethostname(),
            git_commit=commit,
            notes=args.notes,
        )
    _emit(args, run.to_dict(include_series=False), f"started run {run.id}")
    return 0


def _pairs(items: Iterable[str]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for item in items or ():
        key, _, value = item.partition("=")
        if not key:
            _fail(f"expected key=value, got {item!r}")
        out[key] = coerce_value(value)
    return out


def _cmd_log(args: argparse.Namespace) -> int:
    with _open_storage(args) as store:
        run_id = store.resolve_id(args.run)
        params = _pairs(args.param)
        metrics = _pairs(args.metric)
        if params:
            store.log_params(run_id, params)
        if metrics:
            store.log_metrics(run_id, metrics)
        series = _parse_series(args.series)
        points = 0
        for name, pairs in series.items():
            points += store.log_series(run_id, name, pairs)
        if args.tag:
            store.add_tags(run_id, args.tag)
        for artifact in _parse_artifacts(args.artifact):
            store.add_artifact(run_id, artifact["name"], artifact["uri"])
        run = store.get_run(run_id, include_series=False)
    payload = {
        "run": run_id,
        "params": len(params),
        "metrics": len(metrics),
        "series_points": points,
        "tags": len(args.tag),
    }
    _emit(args, payload, f"logged to {run_id}: {len(params)} params, {len(metrics)} metrics, {points} series points")
    return 0


def _cmd_finish(args: argparse.Namespace) -> int:
    with _open_storage(args) as store:
        run = store.finish_run(args.run, status=args.status, notes=args.notes)
    _emit(args, run.to_dict(include_series=False), f"{run.id} -> {run.status}")
    return 0


def _cmd_list(args: argparse.Namespace) -> int:
    with _open_storage(args, create=False) as store:
        runs = store.list_runs(
            experiment=args.experiment,
            status=args.status or None,
            tag=args.tag,
            name_contains=args.name_contains,
            params=_pairs(args.param),
            metrics=_parse_metric_filters(args.metric),
            since=args.since,
            order_by=args.order_by,
            descending=not args.asc,
            limit=args.limit,
            offset=args.offset,
        )
    if args.format == "json" or args.json:
        print(json.dumps([r.to_dict(include_series=False) for r in runs], indent=2, ensure_ascii=False))
        return 0
    if args.format == "csv":
        sys.stdout.write(to_csv(runs))
        return 0
    if args.format == "markdown":
        sys.stdout.write(to_markdown(runs))
        return 0

    if not runs:
        print("no runs match")
        return 0
    config = load_config(Path(args.root) if args.root else Path.cwd())
    metric = config.primary_metric or "accuracy"
    rows = []
    for run in runs:
        value = run.metrics.get(metric)
        rows.append(
            [
                run.id,
                run.experiment,
                run.name or "",
                run.status,
                run.started_at,
                format_value(value) if value is not None else "",
            ]
        )
    _print_table(rows, ["ID", "EXPERIMENT", "NAME", "STATUS", "STARTED", metric])
    return 0


def _cmd_show(args: argparse.Namespace) -> int:
    with _open_storage(args, create=False) as store:
        run = store.get_run(args.run, include_series=not args.no_series)
    if args.json:
        print(json.dumps(run.to_dict(include_series=not args.no_series), indent=2, ensure_ascii=False))
        return 0

    lines = [
        f"{run.id}  [{run.experiment}]  {run.status}",
        f"  name       : {run.name or '-'}",
        f"  started    : {run.started_at}",
        f"  finished   : {run.finished_at or '-'}",
        f"  host       : {run.host or '-'}",
        f"  git_commit : {run.git_commit or '-'}",
        f"  tags       : {', '.join(run.tags) or '-'}",
    ]
    if run.notes:
        lines.append(f"  notes      : {run.notes}")
    if run.params:
        lines.append("  params:")
        for key, value in sorted(run.params.items()):
            lines.append(f"    {key} = {format_value(value)}")
    if run.metrics:
        lines.append("  metrics:")
        for key, value in sorted(run.metrics.items()):
            lines.append(f"    {key} = {format_value(value)}")
    if run.artifacts:
        lines.append("  artifacts:")
        for art in run.artifacts:
            lines.append(f"    {art.name} -> {art.uri}")
    if run.series and not args.no_series:
        lines.append("  series:")
        for name, points in sorted(run.series.items()):
            last = points[-1] if points else (None, None)
            lines.append(
                f"    {name}: {len(points)} points, last step={format_value(last[0])} "
                f"value={format_value(last[1])}"
            )
    print("\n".join(lines))
    return 0


def _cmd_compare(args: argparse.Namespace) -> int:
    root = Path(args.root) if args.root else find_project_root(Path.cwd())
    config = load_config(root)
    with _open_storage(args, create=False) as store:
        runs: List[Run] = [store.get_run(rid) for rid in args.runs]
    comparison = compare_runs(
        runs, metric=args.metric, baseline=args.baseline, config=config, alpha=args.alpha
    )
    if args.json:
        print(json.dumps(comparison.to_dict(), indent=2, ensure_ascii=False))
    else:
        sys.stdout.write(comparison.render_text())
    return 0


def _cmd_export(args: argparse.Namespace) -> int:
    with _open_storage(args, create=False) as store:
        runs = store.list_runs(experiment=args.experiment, limit=args.limit)
    if args.format == "json":
        payload = to_json(runs)
    elif args.format == "markdown":
        payload = to_markdown(runs, metric=args.metric)
    else:
        payload = to_csv(runs)

    if args.out:
        Path(args.out).write_text(payload, encoding="utf-8")
        print(f"wrote {args.out} ({len(runs)} runs)")
    else:
        sys.stdout.write(payload)
    return 0


def _cmd_delete(args: argparse.Namespace) -> int:
    with _open_storage(args, create=False) as store:
        run_id = store.resolve_id(args.run)
        run = store.get_run(run_id, include_series=False)
        if not args.yes:
            answer = input(f"delete {run_id} ({run.experiment})? [y/N] ").strip().lower()
            if answer not in ("y", "yes"):
                print("aborted")
                return 1
        store.delete_run(run_id)
    print(f"deleted {run_id}")
    return 0


def _cmd_stats(args: argparse.Namespace) -> int:
    with _open_storage(args, create=False) as store:
        overview = store.overview()
        experiments = store.experiments()
    if args.json:
        print(json.dumps({"overview": overview, "experiments": experiments}, indent=2))
        return 0
    print(f"runs       : {overview['runs']} (running {overview['running']}, "
          f"finished {overview['finished']}, failed {overview['failed']})")
    print(f"experiments: {overview['experiments']}")
    print(f"metrics    : {', '.join(overview['metrics']) or '-'}")
    print(f"schema     : v{overview['schema_version']}")
    if experiments:
        print()
        _print_table(
            [[e["experiment"], e["runs"], e["finished"], e["failed"], e["last_started"] or "-"] for e in experiments],
            ["EXPERIMENT", "RUNS", "FINISHED", "FAILED", "LAST"],
        )
    return 0


def _cmd_serve(args: argparse.Namespace) -> int:
    from .api.server import serve

    db_path = _resolve_db(args)
    if not db_path.exists():
        print(f"error: no database at {db_path}; run 'lablog init' first", file=sys.stderr)
        return 2
    root = Path(args.root) if args.root else find_project_root(db_path.parent)
    serve(db_path, host=args.host, port=args.port, root=root)
    return 0


HANDLERS = {
    "init": _cmd_init,
    "start": _cmd_start,
    "log": _cmd_log,
    "finish": _cmd_finish,
    "list": _cmd_list,
    "show": _cmd_show,
    "compare": _cmd_compare,
    "export": _cmd_export,
    "delete": _cmd_delete,
    "stats": _cmd_stats,
    "serve": _cmd_serve,
}


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    handler = HANDLERS.get(args.command)
    if handler is None:  # pragma: no cover - argparse enforces valid commands
        parser.error(f"unknown command {args.command!r}")
        return 2
    try:
        return handler(args)
    except KeyError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
