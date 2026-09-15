"""Project configuration: ``experiments.toml`` parsing and metric goals."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

__all__ = ["ProjectConfig", "MetricSpec", "load_config", "CONFIG_FILENAME"]

CONFIG_FILENAME = "experiments.toml"
_GOALS = ("maximize", "minimize", "track")


@dataclass
class MetricSpec:
    """How a metric should be interpreted when comparing runs."""

    name: str
    goal: str = "maximize"
    unit: str = ""
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "goal": self.goal,
            "unit": self.unit,
            "description": self.description,
        }


@dataclass
class ProjectConfig:
    """Parsed ``experiments.toml``."""

    name: str = "untitled"
    description: str = ""
    primary_metric: Optional[str] = None
    metrics: Dict[str, MetricSpec] = field(default_factory=dict)
    path: Optional[Path] = None

    def goal_for(self, metric: str) -> str:
        spec = self.metrics.get(metric)
        return spec.goal if spec else "maximize"

    def is_better(self, metric: str, candidate: float, reference: float) -> bool:
        goal = self.goal_for(metric)
        if goal == "minimize":
            return candidate < reference
        return candidate > reference

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "primary_metric": self.primary_metric,
            "metrics": {k: v.to_dict() for k, v in self.metrics.items()},
        }


def _parse_metrics(raw: Mapping[str, Any]) -> Dict[str, MetricSpec]:
    specs: Dict[str, MetricSpec] = {}
    for name, value in (raw or {}).items():
        if isinstance(value, Mapping):
            goal = str(value.get("goal", "maximize")).lower()
            unit = str(value.get("unit", ""))
            description = str(value.get("description", ""))
        else:
            goal = str(value).lower()
            unit = ""
            description = ""
        if goal not in _GOALS:
            raise ValueError(f"metric {name!r} has invalid goal {goal!r}; use one of {_GOALS}")
        specs[name] = MetricSpec(name=name, goal=goal, unit=unit, description=description)
    return specs


def load_config(root: Path | str, filename: str = CONFIG_FILENAME) -> ProjectConfig:
    """Load ``experiments.toml`` from ``root``.

    A missing file is not an error - lablog works fine with plain defaults, so
    a project can start out with zero configuration.
    """
    directory = Path(root)
    if directory.is_file():
        directory = directory.parent
    config_path = directory / filename
    if not config_path.is_file():
        return ProjectConfig(path=None)

    with open(config_path, "rb") as handle:
        data = tomllib.load(handle)

    project = data.get("project", {}) or {}
    config = ProjectConfig(
        name=str(project.get("name", directory.name)),
        description=str(project.get("description", "")),
        primary_metric=project.get("primary_metric"),
        metrics=_parse_metrics(data.get("metrics", {}) or {}),
        path=config_path,
    )
    if config.primary_metric and config.primary_metric not in config.metrics:
        config.metrics.setdefault(
            config.primary_metric, MetricSpec(name=config.primary_metric, goal="maximize")
        )
    return config
