"""Human-readable metadata for the candidate cell zoo."""

from __future__ import annotations

from dataclasses import dataclass

from .cells import (
    ExperimentalCell,
    NGEnergyMax1,
    NGEnergyMax2,
    NGLagMean1,
    NGShiftCompareMul,
    NGStateMinU1,
)


@dataclass(frozen=True)
class CellCard:
    name: str
    constructor: type[ExperimentalCell]
    state: str
    main_strength: str
    principal_limit: str
    status: str


CELL_CARDS: dict[str, CellCard] = {
    "NG-StateMin-U1": CellCard(
        "NG-StateMin-U1",
        NGStateMinU1,
        "one scalar per coordinate",
        "exact non-attenuating period-two branch",
        "severe odd/even phase dependence",
        "specialized oscillatory memory",
    ),
    "NG-ShiftCompare-Mul": CellCard(
        "NG-ShiftCompare-Mul",
        NGShiftCompareMul,
        "one scalar per coordinate",
        "richer multiplicative nonlinear processing",
        "period-two attractor and vanishing long products",
        "expressive specialized comparator",
    ),
    "NG-EnergyMax-1": CellCard(
        "NG-EnergyMax-1",
        NGEnergyMax1,
        "previous input vector",
        "global energy modulation and two-frame comparison",
        "strict one-step memory and quadratic amplitude growth",
        "two-frame operator",
    ),
    "NG-EnergyMax-2": CellCard(
        "NG-EnergyMax-2",
        NGEnergyMax2,
        "one scalar per coordinate",
        "stable sparse event/extremum memory",
        "poor representation of ordered dense sequences",
        "promising event-memory primitive",
    ),
    "NG-LagMean-1": CellCard(
        "NG-LagMean-1",
        NGLagMean1,
        "one scalar per sample",
        "rank-one delayed multiplicative modulation",
        "one-step horizon; blind to mean-zero directions",
        "collective lag modulator",
    ),
}


def make_cell(name: str, **kwargs: object) -> ExperimentalCell:
    """Instantiate a registered cell by its public name."""
    try:
        card = CELL_CARDS[name]
    except KeyError as exc:
        choices = ", ".join(CELL_CARDS)
        raise KeyError(f"unknown cell {name!r}; choose from: {choices}") from exc
    return card.constructor(**kwargs)
