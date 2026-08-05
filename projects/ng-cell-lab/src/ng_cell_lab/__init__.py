"""NG Cell Lab: experimental recurrent and collective neural primitives."""

from .cells import (
    ExperimentalCell,
    NGEnergyMax1,
    NGEnergyMax2,
    NGLagMean1,
    NGShiftCompareMul,
    NGStateMinU1,
)
from .mlp import NGTriSpeciesMLP, allocate_species_sizes, signed_log1p
from .registry import CELL_CARDS, CellCard, make_cell
from .sequence import NGSequenceLayer

__all__ = [
    "CELL_CARDS",
    "CellCard",
    "ExperimentalCell",
    "NGEnergyMax1",
    "NGEnergyMax2",
    "NGLagMean1",
    "NGTriSpeciesMLP",
    "NGSequenceLayer",
    "NGShiftCompareMul",
    "NGStateMinU1",
    "allocate_species_sizes",
    "make_cell",
    "signed_log1p",
]
