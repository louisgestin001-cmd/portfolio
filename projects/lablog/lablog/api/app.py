"""A dependency-free HTTP application: JSON API plus the static dashboard.

The app is intentionally a plain callable object rather than a framework:

* :meth:`LablogApp.handle` takes a method, path, query mapping and raw body and
  returns a :class:`Response`.  That makes it trivially unit-testable without
  spinning up a socket, and it keeps lablog importable in environments where
  installing a web framework is not allowed.
"""

from __future__ import annotations

import json
import mimetypes
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple
from urllib.parse import parse_qs, urlparse

from ..compare import compare_runs
from ..config import load_config
from ..export import to_csv, to_json, to_markdown
from ..storage import RunNotFound, Storage

__all__ = ["Response", "LablogApp", "build_app", "STATIC_DIR"]

STATIC_DIR = Path(__file__).parent / "static"

_JSON = "application/json; charset=utf-8"


@dataclass
class Response:
    status: int = 200
    body: bytes = b""
    content_type: str = _JSON
    headers: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def json(cls, payload: Any, status: int = 200) -> "Response":
        return cls(
            status=status,
            body=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            content_type=_JSON,
        )

    @classmethod
    def error(cls, message: str, status: int = 400) -> "Response":
        return cls.json({"error": message, "status": status}, status=status)

    @classmethod
    def text(cls, body: str, content_type: str = "text/plain; charset=utf-8", status: int = 200) -> "Response":
        return cls(status=status, body=body.encode("utf-8"), content_type=content_type)


def _as_int(value: Any, default: Optional[int]) -> Optional[int]:
    if value in (None, ""):
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _as_bool(value: Any, default: bool = False) -> bool:
    if value in (None, ""):
        return default
    return str(value).lower() in ("1", "true", "yes", "on")


class LablogApp:
    """Router + handlers for the lablog HTTP surface."""

    def __init__(self, db_path: Path | str, *, root: Optional[Path | str] = None,
                 static_dir: Optional[Path] = None, storage_factory: Callable[..., Storage] = Storage):
        self.db_path = Path(db_path)
        self.root = Path(root) if root else self.db_path.parent.parent
        self.static_dir = Path(static_dir) if static_dir else STATIC_DIR
        self.storage_factory = storage_factory
        self.routes: List[Tuple[str, re.Pattern[str], Callable[..., Response]]] = [
            ("GET", re.compile(r"^/api/health$"), self.health),
            ("GET", re.compile(r"^/api/overview$"), self.overview),
            ("GET", re.compile(r"^/api/experiments$"), self.list_experiments),
            ("GET", re.compile(r"^/api/runs$"), self.list_runs),
            ("POST", re.compile(r"^/api/runs$"), self.create_run),
            ("GET", re.compile(r"^/api/runs/(?P<run_id>[^/]+)$"), self.get_run),
            ("PATCH", re.compile(r"^/api/runs/(?P<run_id>[^/]+)$"), self.patch_run),
            ("DELETE", re.compile(r"^/api/runs/(?P<run_id>[^/]+)$"), self.delete_run),
            ("GET", re.compile(r"^/api/runs/(?P<run_id>[^/]+)/series$"), self.get_series),
            ("POST", re.compile(r"^/api/runs/(?P<run_id>[^/]+)/series$"), self.post_series),
            ("GET", re.compile(r"^/api/compare$"), self.compare),
            ("GET", re.compile(r"^/api/export$"), self.export),
        ]

    # ---------------------------------------------------------------- plumbing
    def _store(self, *, create: bool = False) -> Storage:
        return self.storage_factory(self.db_path, create=create)

    def handle(
        self,
        method: str,
        target: str,
        body: bytes = b"",
        *,
        query: Optional[Dict[str, List[str]]] = None,
    ) -> Response:
        parsed = urlparse(target)
        if query is None:
            query = parse_qs(parsed.query, keep_blank_values=True)
        path = parsed.path or "/"
        method = method.upper()

        if method == "OPTIONS":
            return Response(status=204, body=b"", content_type="text/plain")

        if path.startswith("/api/"):
            for route_method, pattern, handler in self.routes:
                if route_method != method:
                    continue
                match = pattern.match(path)
                if match:
                    try:
                        return handler(match.groupdict(), query, body)
                    except RunNotFound as exc:
                        return Response.error(str(exc), status=404)
                    except json.JSONDecodeError as exc:
                        return Response.error(f"invalid JSON body: {exc}", status=400)
                    except ValueError as exc:
                        return Response.error(str(exc), status=400)
            return Response.error(f"no route for {method} {path}", status=404)

        return self._static(path)

    def _static(self, path: str) -> Response:
        relative = "index.html" if path in ("/", "") else path.lstrip("/")
        if relative.startswith("static/"):
            relative = relative[len("static/"):]
        candidate = (self.static_dir / relative).resolve()
        try:
            candidate.relative_to(self.static_dir.resolve())
        except ValueError:
            return Response.error("forbidden", status=403)
        if not candidate.is_file():
            return Response.error("not found", status=404)
        content_type, _ = mimetypes.guess_type(str(candidate))
        return Response(
            status=200,
            body=candidate.read_bytes(),
            content_type=content_type or "application/octet-stream",
        )

    # ---------------------------------------------------------------- handlers
    def health(self, params: Dict[str, str], query: Dict[str, List[str]], body: bytes) -> Response:
        return Response.json({"status": "ok", "db": str(self.db_path), "exists": self.db_path.exists()})

    def overview(self, params, query, body) -> Response:
        with self._store() as store:
            return Response.json(store.overview())

    def list_experiments(self, params, query, body) -> Response:
        with self._store() as store:
            return Response.json(store.experiments())

    def list_runs(self, params, query, body) -> Response:
        def q(name: str, default: Any = None) -> Any:
            values = query.get(name)
            return values[0] if values else default

        status_values = query.get("status") or None
        with self._store() as store:
            runs = store.list_runs(
                experiment=q("experiment"),
                status=status_values,
                tag=q("tag"),
                name_contains=q("name_contains"),
                since=q("since"),
                order_by=q("order_by", "started_at"),
                descending=not _as_bool(q("asc"), False),
                limit=_as_int(q("limit"), None),
                offset=_as_int(q("offset"), 0) or 0,
            )
            return Response.json([r.to_dict(include_series=False) for r in runs])

    def create_run(self, params, query, body) -> Response:
        payload = self._json_body(body)
        experiment = payload.get("experiment")
        if not experiment:
            return Response.error("field 'experiment' is required", status=400)
        with self._store(create=True) as store:
            run = store.create_run(
                str(experiment),
                name=payload.get("name"),
                params=payload.get("params") or {},
                tags=payload.get("tags") or [],
                notes=payload.get("notes"),
                host=payload.get("host"),
                git_commit=payload.get("git_commit"),
                status=payload.get("status", "running"),
            )
            metrics = payload.get("metrics") or {}
            if metrics:
                store.log_metrics(run.id, metrics)
            for name, points in (payload.get("series") or {}).items():
                store.log_series(run.id, name, points)
            created = store.get_run(run.id, include_series=False)
        return Response.json(created.to_dict(include_series=False), status=201)

    def get_run(self, params, query, body) -> Response:
        include_series = _as_bool((query.get("series") or ["1"])[0], True)
        with self._store() as store:
            run = store.get_run(params["run_id"], include_series=include_series)
        return Response.json(run.to_dict(include_series=include_series))

    def patch_run(self, params, query, body) -> Response:
        payload = self._json_body(body)
        scalar = {k: v for k, v in payload.items()
                  if k in ("name", "status", "notes", "host", "git_commit", "experiment")}
        with self._store() as store:
            run_id = store.resolve_id(params["run_id"])
            if scalar:
                store.update_run(run_id, **scalar)
            if payload.get("params"):
                store.log_params(run_id, payload["params"])
            if payload.get("metrics"):
                store.log_metrics(run_id, payload["metrics"])
            if payload.get("tags"):
                store.add_tags(run_id, payload["tags"])
            if payload.get("remove_tags"):
                for tag in payload["remove_tags"]:
                    store.remove_tag(run_id, tag)
            for name, points in (payload.get("series") or {}).items():
                store.log_series(run_id, name, points)
            run = store.get_run(run_id, include_series=False)
        return Response.json(run.to_dict(include_series=False))

    def delete_run(self, params, query, body) -> Response:
        with self._store() as store:
            run_id = store.resolve_id(params["run_id"])
            store.delete_run(run_id)
        return Response.json({"deleted": run_id})

    def get_series(self, params, query, body) -> Response:
        name = (query.get("name") or [None])[0]
        with self._store() as store:
            series = store.series(params["run_id"], name)
        return Response.json(series)

    def post_series(self, params, query, body) -> Response:
        payload = self._json_body(body)
        name = payload.get("name")
        points = payload.get("points") or []
        if not name:
            return Response.error("field 'name' is required", status=400)
        with self._store() as store:
            count = store.log_series(params["run_id"], name, points)
        return Response.json({"run": params["run_id"], "name": name, "points": count}, status=201)

    def compare(self, params, query, body) -> Response:
        ids_raw = (query.get("ids") or [""])[0]
        ids = [part for part in re.split(r"[,\s]+", ids_raw) if part]
        if len(ids) < 2:
            return Response.error("provide at least two run ids via ?ids=a,b", status=400)
        metric = (query.get("metric") or [None])[0]
        baseline = (query.get("baseline") or [None])[0]
        alpha = float((query.get("alpha") or ["0.05"])[0])
        config = load_config(self.root)
        with self._store() as store:
            runs = [store.get_run(rid) for rid in ids]
        comparison = compare_runs(runs, metric=metric, baseline=baseline, config=config, alpha=alpha)
        payload = comparison.to_dict()
        payload["text"] = comparison.render_text()
        return Response.json(payload)

    def export(self, params, query, body) -> Response:
        fmt = (query.get("format") or ["json"])[0]
        experiment = (query.get("experiment") or [None])[0]
        limit = _as_int((query.get("limit") or [None])[0], None)
        metric = (query.get("metric") or [None])[0]
        with self._store() as store:
            runs = store.list_runs(experiment=experiment, limit=limit)
        if fmt == "csv":
            return Response.text(to_csv(runs), content_type="text/csv; charset=utf-8")
        if fmt == "markdown":
            return Response.text(to_markdown(runs, metric=metric), content_type="text/markdown; charset=utf-8")
        return Response.text(to_json(runs), content_type=_JSON)

    @staticmethod
    def _json_body(body: bytes) -> Dict[str, Any]:
        if not body:
            return {}
        data = json.loads(body.decode("utf-8"))
        if not isinstance(data, dict):
            raise ValueError("request body must be a JSON object")
        return data


def build_app(db_path: Path | str, *, root: Optional[Path | str] = None,
              static_dir: Optional[Path] = None) -> LablogApp:
    return LablogApp(db_path, root=root, static_dir=static_dir)
