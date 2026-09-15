"""Statistics engine implemented with the standard library only.

Everything here is deliberately explicit and testable: descriptive summaries,
Welch's unequal-variance t-test (via the regularised incomplete beta function),
Cohen's d effect size, and a small bootstrap confidence interval helper.

The incomplete beta continued fraction follows the classic Lentz-style
recurrence used by Numerical Recipes; the two-sided p-value for the t
distribution is ``I_{df/(df+t^2)}(df/2, 1/2)``.
"""

from __future__ import annotations

import math
import random
from typing import Dict, Iterable, List, Optional, Sequence

__all__ = [
    "mean",
    "variance",
    "stddev",
    "median",
    "quantile",
    "describe",
    "students_t_two_sided_p",
    "welch_ttest",
    "cohen_d",
    "bootstrap_ci",
    "effect_label",
]

_TINY = 3e-12
_FPMIN = 1e-300


def _as_floats(values: Iterable[float]) -> List[float]:
    return [float(v) for v in values]


def mean(values: Iterable[float]) -> float:
    data = _as_floats(values)
    if not data:
        raise ValueError("mean() requires at least one value")
    return math.fsum(data) / len(data)


def variance(values: Iterable[float]) -> float:
    """Unbiased sample variance (``n - 1`` denominator)."""
    data = _as_floats(values)
    if len(data) < 2:
        raise ValueError("variance() requires at least two values")
    mu = math.fsum(data) / len(data)
    return math.fsum((x - mu) ** 2 for x in data) / (len(data) - 1)


def stddev(values: Iterable[float]) -> float:
    return math.sqrt(variance(values))


def median(values: Iterable[float]) -> float:
    return quantile(values, 0.5)


def quantile(values: Iterable[float], q: float) -> float:
    """Linear-interpolation quantile (numpy's default ``linear`` method)."""
    if not 0.0 <= q <= 1.0:
        raise ValueError("q must be within [0, 1]")
    data = sorted(_as_floats(values))
    if not data:
        raise ValueError("quantile() requires at least one value")
    if len(data) == 1:
        return data[0]
    position = q * (len(data) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return data[int(position)]
    weight = position - lower
    return data[lower] * (1.0 - weight) + data[upper] * weight


def describe(values: Iterable[float]) -> Dict[str, Optional[float]]:
    data = _as_floats(values)
    if not data:
        return {
            "n": 0,
            "mean": None,
            "std": None,
            "min": None,
            "q25": None,
            "median": None,
            "q75": None,
            "max": None,
        }
    return {
        "n": len(data),
        "mean": mean(data),
        "std": stddev(data) if len(data) > 1 else 0.0,
        "min": min(data),
        "q25": quantile(data, 0.25),
        "median": median(data),
        "q75": quantile(data, 0.75),
        "max": max(data),
    }


def _betacf(a: float, b: float, x: float) -> float:
    qab = a + b
    qap = a + 1.0
    qam = a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < _FPMIN:
        d = _FPMIN
    d = 1.0 / d
    h = d
    for m in range(1, 300):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < _FPMIN:
            d = _FPMIN
        c = 1.0 + aa / c
        if abs(c) < _FPMIN:
            c = _FPMIN
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < _FPMIN:
            d = _FPMIN
        c = 1.0 + aa / c
        if abs(c) < _FPMIN:
            c = _FPMIN
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < _TINY:
            break
    return h


def _betai(a: float, b: float, x: float) -> float:
    """Regularised incomplete beta function ``I_x(a, b)``."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    log_bt = (
        math.lgamma(a + b)
        - math.lgamma(a)
        - math.lgamma(b)
        + a * math.log(x)
        + b * math.log1p(-x)
    )
    bt = math.exp(log_bt)
    if x < (a + 1.0) / (a + b + 2.0):
        return bt * _betacf(a, b, x) / a
    return 1.0 - bt * _betacf(b, a, 1.0 - x) / b


def students_t_two_sided_p(t: float, df: float) -> float:
    """Two-sided p-value ``P(|T_df| >= |t|)``."""
    if df <= 0:
        raise ValueError("df must be positive")
    t = abs(float(t))
    if math.isinf(t):
        return 0.0
    x = df / (df + t * t)
    return _betai(df / 2.0, 0.5, x)


def welch_ttest(a: Iterable[float], b: Iterable[float]) -> Dict[str, float]:
    """Welch's unequal-variance two-sample t-test.

    Returns ``{"t", "df", "p"}``.  Two constant-but-different samples would
    divide by zero, so the guard returns ``p = 0.0`` when there is no spread
    and the means differ, and ``p = 1.0`` when the samples are identical.
    """
    sample_a = _as_floats(a)
    sample_b = _as_floats(b)
    if len(sample_a) < 2 or len(sample_b) < 2:
        raise ValueError("welch_ttest() requires at least two values per sample")

    na, nb = len(sample_a), len(sample_b)
    ma, mb = mean(sample_a), mean(sample_b)
    va, vb = variance(sample_a), variance(sample_b)

    se_squared = va / na + vb / nb
    if se_squared <= 0.0:
        if ma == mb:
            return {"t": 0.0, "df": float(na + nb - 2), "p": 1.0}
        return {"t": math.inf if ma > mb else -math.inf, "df": float(na + nb - 2), "p": 0.0}

    t = (ma - mb) / math.sqrt(se_squared)
    numerator = se_squared ** 2
    denominator = (va / na) ** 2 / (na - 1) + (vb / nb) ** 2 / (nb - 1)
    df = numerator / denominator
    return {"t": t, "df": df, "p": students_t_two_sided_p(t, df)}


def cohen_d(a: Iterable[float], b: Iterable[float]) -> float:
    """Cohen's d using the pooled standard deviation."""
    sample_a = _as_floats(a)
    sample_b = _as_floats(b)
    if len(sample_a) < 2 or len(sample_b) < 2:
        raise ValueError("cohen_d() requires at least two values per sample")
    na, nb = len(sample_a), len(sample_b)
    va, vb = variance(sample_a), variance(sample_b)
    pooled = math.sqrt(((na - 1) * va + (nb - 1) * vb) / (na + nb - 2))
    if pooled == 0.0:
        return 0.0
    return (mean(sample_a) - mean(sample_b)) / pooled


def effect_label(d: float) -> str:
    """Conventional (if arbitrary) thresholds for |d|."""
    magnitude = abs(d)
    if magnitude < 0.2:
        return "negligible"
    if magnitude < 0.5:
        return "small"
    if magnitude < 0.8:
        return "medium"
    return "large"


def bootstrap_ci(
    values: Sequence[float],
    *,
    statistic=mean,
    confidence: float = 0.95,
    iterations: int = 2000,
    seed: int = 1234,
) -> Dict[str, float]:
    """Percentile bootstrap confidence interval for a statistic."""
    data = _as_floats(values)
    if len(data) < 2:
        raise ValueError("bootstrap_ci() requires at least two values")
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence must be within (0, 1)")

    rng = random.Random(seed)
    n = len(data)
    estimates = []
    for _ in range(iterations):
        sample = [data[rng.randrange(n)] for _ in range(n)]
        estimates.append(statistic(sample))
    alpha = (1.0 - confidence) / 2.0
    return {
        "low": quantile(estimates, alpha),
        "high": quantile(estimates, 1.0 - alpha),
        "confidence": confidence,
        "iterations": iterations,
    }
