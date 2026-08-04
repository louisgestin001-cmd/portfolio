"""PyTorch implementation of NG-StateMin-U1.

The scalar law is

    s_t = y_t = min(x_t - s_{t-1}, -x_t)

and is applied elementwise to hidden coordinates.
"""

from __future__ import annotations

import torch
from torch import Tensor, nn


def ng_state_min_u1(x_t: Tensor, state: Tensor) -> Tensor:
    """Apply the NG-StateMin-U1 transition elementwise.

    Args:
        x_t: Current preactivation, shaped ``(..., hidden_size)``.
        state: Previous state with the same shape as ``x_t``.

    Returns:
        The next state, which is also the emitted signal.
    """
    if x_t.shape != state.shape:
        raise ValueError(
            f"x_t and state must have identical shapes, got {x_t.shape} and {state.shape}"
        )
    return torch.minimum(x_t - state, -x_t)


class NGStateMinU1Cell(nn.Module):
    """Parameter-free recurrent transition for a precomputed preactivation."""

    def forward(self, x_t: Tensor, state: Tensor) -> Tensor:
        return ng_state_min_u1(x_t, state)


class NGStateMinU1Layer(nn.Module):
    """A small recurrent layer with a learned input projection.

    Only the input projection is learned internally. The recurrent law itself
    has no learned coefficient or recurrent matrix.
    """

    def __init__(self, input_size: int, hidden_size: int, *, bias: bool = True) -> None:
        super().__init__()
        if input_size <= 0 or hidden_size <= 0:
            raise ValueError("input_size and hidden_size must be positive")
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.input_projection = nn.Linear(input_size, hidden_size, bias=bias)
        self.cell = NGStateMinU1Cell()

    def forward(
        self, sequence: Tensor, initial_state: Tensor | None = None
    ) -> tuple[Tensor, Tensor]:
        """Run a batch-first sequence through the recurrent law.

        Args:
            sequence: Tensor of shape ``(batch, time, input_size)``.
            initial_state: Optional tensor of shape ``(batch, hidden_size)``.

        Returns:
            ``(outputs, final_state)`` where outputs has shape
            ``(batch, time, hidden_size)``.
        """
        if sequence.ndim != 3:
            raise ValueError("sequence must have shape (batch, time, input_size)")
        if sequence.size(-1) != self.input_size:
            raise ValueError(
                f"expected input_size={self.input_size}, got {sequence.size(-1)}"
            )

        batch_size = sequence.size(0)
        if initial_state is None:
            state = sequence.new_zeros(batch_size, self.hidden_size)
        else:
            expected = (batch_size, self.hidden_size)
            if tuple(initial_state.shape) != expected:
                raise ValueError(
                    f"initial_state must have shape {expected}, got {tuple(initial_state.shape)}"
                )
            state = initial_state

        projected = self.input_projection(sequence)
        outputs: list[Tensor] = []
        for x_t in projected.unbind(dim=1):
            state = self.cell(x_t, state)
            outputs.append(state)

        if outputs:
            stacked = torch.stack(outputs, dim=1)
        else:
            stacked = projected.new_empty(batch_size, 0, self.hidden_size)
        return stacked, state
