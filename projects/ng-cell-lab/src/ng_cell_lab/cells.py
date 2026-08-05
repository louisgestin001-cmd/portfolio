"""Experimental recurrent cells collected in NG Cell Lab.

All cells expose a common step API::

    output, next_state = cell(x_t, previous_state)

where ``x_t`` is shaped ``[..., hidden_dim]``. These are research
primitives, not drop-in claims of state-of-the-art recurrent models.
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod

import torch
from torch import Tensor, nn


class ExperimentalCell(nn.Module, ABC):
    """Base class for elementwise or collectively modulated cells."""

    @abstractmethod
    def initial_state(self, x: Tensor) -> Tensor:
        """Return a zero-like initial state compatible with one input step."""

    @abstractmethod
    def forward(self, x: Tensor, state: Tensor) -> tuple[Tensor, Tensor]:
        """Apply one recurrent step and return ``(output, next_state)``."""


class NGStateMinU1(ExperimentalCell):
    r"""Minimal piecewise-linear state law.

    .. math:: s_t = y_t = \min(x_t - s_{t-1}, -x_t)
    """

    def initial_state(self, x: Tensor) -> Tensor:
        return torch.zeros_like(x)

    def forward(self, x: Tensor, state: Tensor) -> tuple[Tensor, Tensor]:
        next_state = torch.minimum(x - state, -x)
        return next_state, next_state


class NGShiftCompareMul(ExperimentalCell):
    r"""Shifted multiplicative recurrent comparator.

    The original experiments used a numerical clamp of ``[-20, 20]``.
    """

    def __init__(self, clip: float = 20.0) -> None:
        super().__init__()
        if clip <= 0:
            raise ValueError("clip must be positive")
        self.clip = float(clip)

    @property
    def shift(self) -> float:
        return 1.231609 * math.sin(1.0) + 0.029583

    def initial_state(self, x: Tensor) -> Tensor:
        return torch.zeros_like(x)

    def forward(self, x: Tensor, state: Tensor) -> tuple[Tensor, Tensor]:
        c = x.new_tensor(self.shift)
        a = 1.164214 * (x - c) - 0.074532
        q = 0.646213 * state - 0.110654
        b = 1.291792 * torch.tanh(q - x) - 0.070705
        next_state = torch.clamp(0.907561 * (a * b) - 0.145458, -self.clip, self.clip)
        return next_state, next_state


class NGEnergyMax1(ExperimentalCell):
    r"""One-step energy-modulated comparison.

    .. math::
       e_t = d^{-1}\sum_j |x_{t,j}|,
       \quad y_t = 0.922865\max(s_{t-1}, 0.839798 e_t x_t),
       \quad s_t = x_t.
    """

    output_scale = 0.922865
    energy_scale = 0.839798

    def initial_state(self, x: Tensor) -> Tensor:
        return torch.zeros_like(x)

    def forward(self, x: Tensor, state: Tensor) -> tuple[Tensor, Tensor]:
        energy = x.abs().mean(dim=-1, keepdim=True)
        current = self.energy_scale * energy * x
        output = self.output_scale * torch.maximum(state, current)
        return output, x


class NGEnergyMax2(ExperimentalCell):
    r"""Stable event/extremum memory derived from EnergyMax-1.

    .. math::
       g_t = e_t/(1+e_t),\quad u_t=0.839798 g_t x_t,
       \quad s_t=\operatorname{ChooseMaxAbs}(\rho s_{t-1}, u_t),
       \quad y_t=0.922865s_t.

    ``rho=0.999`` is the strongest tested default that still permits later
    events to overwrite older equal-scale events through decay.
    """

    output_scale = 0.922865
    energy_scale = 0.839798

    def __init__(self, rho: float = 0.999, use_energy: bool = True) -> None:
        super().__init__()
        if not 0.0 <= rho <= 1.0:
            raise ValueError("rho must be in [0, 1]")
        self.rho = float(rho)
        self.use_energy = bool(use_energy)

    def initial_state(self, x: Tensor) -> Tensor:
        return torch.zeros_like(x)

    @staticmethod
    def choose_max_abs(memory: Tensor, candidate: Tensor) -> Tensor:
        """Choose the value with larger absolute magnitude, preserving sign."""
        return torch.where(memory.abs() >= candidate.abs(), memory, candidate)

    def forward(self, x: Tensor, state: Tensor) -> tuple[Tensor, Tensor]:
        if self.use_energy:
            energy = x.abs().mean(dim=-1, keepdim=True)
            gate: Tensor | float = energy / (1.0 + energy)
        else:
            gate = 1.0
        candidate = self.energy_scale * gate * x
        next_state = self.choose_max_abs(self.rho * state, candidate)
        return self.output_scale * next_state, next_state


class NGLagMean1(ExperimentalCell):
    r"""Rank-one delayed collective modulation.

    State is scalar per sample rather than one value per hidden coordinate.
    """

    def __init__(
        self,
        state_scale: float = 0.5,
        state_bias: float = 0.011376,
        output_bias: float = 0.097814,
        clip: float = 32.0,
    ) -> None:
        super().__init__()
        if clip <= 0:
            raise ValueError("clip must be positive")
        self.state_scale = float(state_scale)
        self.state_bias = float(state_bias)
        self.output_bias = float(output_bias)
        self.clip = float(clip)

    def initial_state(self, x: Tensor) -> Tensor:
        return x.new_zeros(*x.shape[:-1], 1)

    def forward(self, x: Tensor, state: Tensor) -> tuple[Tensor, Tensor]:
        next_state = torch.clamp(
            self.state_scale * x.mean(dim=-1, keepdim=True) + self.state_bias,
            -self.clip,
            self.clip,
        )
        inner = torch.clamp(state * x, -self.clip, self.clip)
        output = torch.clamp(inner - self.output_bias, -self.clip, self.clip)
        return output, next_state
