"""Run comparison engine: parameter diffs, metric tables, deltas and tests."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Sequence

from .config import ProjectConfig
from .models import Run, format_value
from .stats import cohen_d, describe, effect_label, welch_ttest

__all__ = ["Comparison", "compare_runs"]


@dataclass
class Comparison:
    """A structured comparison of two or more runs."""

    metric: Optional[str]
    goal: str
    baseline: Optional[str]
    run_ids: List[str] = field(default_factory=list)
    param_diff: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    shared_params: Dict[str, Any] = field(default_factory=dict)
    metric_table: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    ranking: List[Dict[str, Any]] = field(default_factory=list)
    series_summary: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    significance: Optional[Dict[str, Any]] = None
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metric": self.metric,
            "goal": self.goal,
            "baseline": self.baseline,
            "runs": list(self.run_ids),
            "param_diff": self.param_diff,
            "shared_params": self.shared_params,
            "metric_table": self.metric_table,
            "ranking": self.ranking,
            "series_summary": self.series_summary,
            "significance": self.significance,
            "notes": self.notes,
        }

    def render_text(self) -> str:
        lines: List[str] = []
        lines.append(f"Comparing {len(self.run_ids)} runs")
        if self.metric:
            lines.append(f"Primary metric: {self.metric} (goal: {self.goal})")
        if self.baseline:
            lines.append(f"Baseline: {self.baseline}")
        lines.append("")

        if self.shared_params:
            lines.append("Shared params:")
            for key, value in sorted(self.shared_params.items()):
                lines.append(f"  {key} = {format_value(value)}")
            lines.append("")

        if self.param_diff:
            lines.append("Parameter differences:")
            for key, values in sorted(self.param_diff.items()):
                rendered = ", ".join(
                    f"{rid}={format_value(value)}" for rid, value in values.items()
                )
                lines.append(f"  {key}: {rendered}")
            lines.append("")

        if self.metric_table:
            lines.append("Metrics:")
            for key, values in sorted(self.metric_table.items()):
                rendered = ", ".join(
                    f"{rid}={format_value(value)}" for rid, value in values.items()
                )
                lines.append(f"  {key}: {rendered}")
            lines.append("")

        if self.ranking:
            lines.append(f"Ranking by {self.metric} ({self.goal}):")
            for position, row in enumerate(self.ranking, 1):
                delta = row.get("delta")
                suffix = ""
                if delta is not None and row.get("improved") is not None:
                    rel = row.get("relative_change")
                    marker = "improved" if row.get("improved") else "regressed"
                    rel_txt = f" ({rel:+.1%})" if isinstance(rel, (int, float)) else ""
                    suffix = f"  [{marker} {format_value(delta)}{rel_txt} vs baseline]"
                flag = " *best*" if row.get("best") else ""
                lines.append(
                    f"  {position}. {row['run']} = {format_value(row['value'])}{suffix}{flag}"
                )
            lines.append("")

        if self.series_summary:
            lines.append("Series summary (per run):")
            for rid, stats in self.series_summary.items():
                lines.append(
                    f"  {rid}: n={stats['n']} mean={format_value(stats['mean'])} "
                    f"min={format_value(stats['min'])} max={format_value(stats['max'])} "
                    f"last={format_value(stats['last'])}"
                )
            lines.append("")

        if self.significance:
            sig = self.significance
            lines.append(
                f"Welch t-test ({sig['a']} vs {sig['b']}): t={sig['t']:.3f}, "
                f"df={sig['df']:.2f}, p={sig['p']:.4g} -> "
                f"{'significant' if sig['significant'] else 'not significant'} at alpha={sig['alpha']}"
            )
            lines.append(
                f"  Cohen's d={sig['cohen_d']:.3f} ({sig['effect']}), "
                f"mean_a={format_value(sig['mean_a'])}, mean_b={format_value(sig['mean_b'])}"
            )
        for note in self.notes:
            lines.append(f"note: {note}")
        return "\n".join(lines).rstrip() + "\n"


def _shared_and_diff_params(
    runs: Sequence[Run],
) -> tuple[Dict[str, Any], Dict[str, Dict[str, Any]]]:
    keys: List[str] = []
    for run in runs:
        for key in run.params:
            if key not in keys:
                keys.append(key)

    shared: Dict[str, Any] = {}
    diff: Dict[str, Dict[str, Any]] = {}
    for key in keys:
        values = {run.id: run.params.get(key) for run in runs}
        distinct = {_hashable(v) for v in values.values()}
        if len(distinct) == 1:
            shared[key] = next(iter(values.values()))
        else:
            diff[key] = values
    return shared, diff


def _hashable(value: Any) -> Any:
    if isinstance(value, list):
        return tuple(value)
    return value


def _metric_table(runs: Sequence[Run]) -> Dict[str, Dict[str, Any]]:
    keys: List[str] = []
    for run in runs:
        for key in run.metrics:
            if key not in keys:
                keys.append(key)
    return {key: {run.id: run.metrics.get(key) for run in runs} for key in keys}


def _series_summary(runs: Sequence[Run], metric: str) -> Dict[str, Dict[str, Any]]:
    summary: Dict[str, Dict[str, Any]] = {}
    for run in runs:
        points = run.series.get(metric)
        if not points:
            continue
        values = [value for _, value in points]
        stats = describe(values)
        stats["last"] = values[-1]
        stats["first"] = values[0]
        summary[run.id] = stats
    return summary


def _is_better(goal: str, candidate: float, reference: float) -> bool:
    return candidate < reference if goal == "minimize" else candidate > reference


def compare_runs(
    runs: Sequence[Run],
    *,
    metric: Optional[str] = None,
    baseline: Optional[str] = None,
    config: Optional[ProjectConfig] = None,
    alpha: float = 0.05,
) -> Comparison:
    """Compare ``runs`` and return a :class:`Comparison`.

    ``metric`` defaults to the project's primary metric, else the first metric
    present in every run, else the first metric found.  ``baseline`` may be a
    run id, an unambiguous id prefix, or a 0-based index into ``runs``;
    it defaults to the best run by the chosen metric.
    """
    if len(runs) < 2:
        raise ValueError("compare_runs() needs at least two runs")

    notes: List[str] = []
    goal = config.goal_for(metric) if (config and metric) else "maximize"

    if metric is None:
        if config and config.primary_metric:
            metric = config.primary_metric
        else:
            common = [key for key in runs[0].metrics if all(key in r.metrics for r in runs)]
            metric = (common or list(_metric_table(runs)) or [None])[0]
            if metric:
                notes.append(f"no explicit metric given; defaulted to {metric!r}")

    if config and metric:
        goal = config.goal_for(metric)

    shared, diff = _shared_and_diff_params(runs)
    table = _metric_table(runs)
    series_summary = _series_summary(runs, metric) if metric else {}

    ranking: List[Dict[str, Any]] = []
    if metric and any(metric in r.metrics for r in runs):
        scored = [
            (run, float(run.metrics[metric]))
            for run in runs
            if isinstance(run.metrics.get(metric), (int, float))
            and not isinstance(run.metrics.get(metric), bool)
        ]
        if len(scored) < len(runs):
            missing = [r.id for r in runs if r not in {s[0] for s in scored}]
            notes.append(
                "runs without a numeric value for "
                f"{metric!r}: {', '.join(missing)}"
            )

        reverse = goal != "minimize"
        ordered = sorted(scored, key=lambda item: item[1], reverse=reverse)

        resolved_baseline: Optional[str] = None
        if baseline is None:
            resolved_baseline = ordered[0][0].id if ordered else None
        else:
            resolved_baseline = _resolve_baseline(baseline, runs, scored)
        if resolved_baseline is None and ordered:
            resolved_baseline = ordered[0][0].id
            notes.append("baseline could not be resolved; using the best run")

        baseline_value = None
        for run, value in scored:
            if run.id == resolved_baseline:
                baseline_value = value
                break

        for run, value in ordered:
            delta = None
            relative = None
            improved = None
            if baseline_value is not None:
                delta = value - baseline_value
                if baseline_value not in (0, 0.0):
                    relative = delta / abs(baseline_value)
                improved = _is_better(goal, value, baseline_value) if run.id != resolved_baseline else None
            ranking.append(
                {
                    "run": run.id,
                    "name": run.display_name,
                    "experiment": run.experiment,
                    "value": value,
                    "delta": delta,
                    "relative_change": relative,
                    "improved": improved,
                    "best": bool(ordered) and run.id == ordered[0][0].id,
                    "baseline": run.id == resolved_baseline,
                }
            )

    significance: Optional[Dict[str, Any]] = None
    if metric and len(series_summary) >= 2 and ranking:
        best_id = ranking[0]["run"]
        base_id = next((row["run"] for row in ranking if row.get("baseline")), None)
        if base_id == best_id and len(ranking) > 1:
            # The default baseline is the best run, so testing best-vs-baseline
            # would be meaningless.  Fall back to the runner-up, which is the
            # comparison a reader actually wants: "is the winner real?"
            base_id = ranking[1]["run"]
            notes.append(
                "no explicit baseline; the significance test compares the best run "
                f"against the runner-up ({base_id})"
            )
        if best_id and base_id and best_id != base_id:
            series_a = [v for _, v in runs[_index_of(runs, best_id)].series.get(metric, [])]
            series_b = [v for _, v in runs[_index_of(runs, base_id)].series.get(metric, [])]
            if len(series_a) >= 2 and len(series_b) >= 2:
                test = welch_ttest(series_a, series_b)
                d = cohen_d(series_a, series_b)
                significance = {
                    "a": best_id,
                    "b": base_id,
                    "metric": metric,
                    "t": test["t"],
                    "df": test["df"],
                    "p": test["p"],
                    "alpha": alpha,
                    "significant": test["p"] < alpha,
                    "cohen_d": d,
                    "effect": effect_label(d),
                    "mean_a": sum(series_a) / len(series_a),
                    "mean_b": sum(series_b) / len(series_b),
                    "n_a": len(series_a),
                    "n_b": len(series_b),
                }
            else:
                notes.append("not enough series points for a significance test")

    if not metric:
        notes.append("no metrics recorded in these runs")

    comparison = Comparison(
        metric=metric,
        goal=goal,
        baseline=(ranking and next((r["run"] for r in ranking if r.get("baseline")), None)) or None,
        run_ids=[run.id for run in runs],
        param_diff=diff,
        shared_params=shared,
        metric_table=table,
        ranking=ranking,
        series_summary=series_summary,
        significance=significance,
        notes=notes,
    )
    return comparison


def _index_of(runs: Sequence[Run], run_id: str) -> int:
    for index, run in enumerate(runs):
        if run.id == run_id:
            return index
    raise KeyError(run_id)


def _resolve_baseline(
    baseline: str, runs: Sequence[Run], scored: Sequence[tuple[Run, float]]
) -> Optional[str]:
    for run, _ in scored:
        if run.id == baseline:
            return run.id
    for run, _ in scored:
        if run.id.startswith(baseline):
            return run.id
    if baseline.isdigit():
        index = int(baseline)
        if 0 <= index < len(runs):
            return runs[index].id
    return None
