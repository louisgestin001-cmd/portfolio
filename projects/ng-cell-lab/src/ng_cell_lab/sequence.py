"""Sequence wrappers for NG Cell Lab cells."""

from __future__ import annotations

import torch
from torch import Tensor, nn

from .cells import ExperimentalCell


class NGSequenceLayer(nn.Module):
    """Scan an experimental cell over a batch-first sequence.

    Parameters
    ----------
    cell:
        A cell following the common ``(x, state) -> (y, next_state)`` API.
    return_sequence:
        Return every output when true, otherwise only the final output.
    """

    def __init__(self, cell: ExperimentalCell, return_sequence: bool = True) -> None:
        super().__init__()
        self.cell = cell
        self.return_sequence = bool(return_sequence)

    def forward(
        self,
        sequence: Tensor,
        state: Tensor | None = None,
    ) -> tuple[Tensor, Tensor]:
        if sequence.ndim < 3:
            raise ValueError("sequence must have shape [batch, time, hidden]")
        if sequence.shape[1] == 0:
            raise ValueError("sequence length must be positive")

        first = sequence[:, 0]
        current_state = self.cell.initial_state(first) if state is None else state
        outputs: list[Tensor] = []
        output = torch.empty_like(first)
        for step in sequence.unbind(dim=1):
            output, current_state = self.cell(step, current_state)
            outputs.append(output)

        if self.return_sequence:
            return torch.stack(outputs, dim=1), current_state
        return output, current_state
