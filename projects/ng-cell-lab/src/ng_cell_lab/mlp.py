"""Heterogeneous feed-forward blocks collected in NG Cell Lab."""

from __future__ import annotations

from collections.abc import Sequence

import torch
from torch import Tensor, nn


def signed_log1p(x: Tensor) -> Tensor:
    """Odd, softly compressive ``log(1 + |x|)`` transform.

    ``torch.where`` is used instead of ``sign(x) * log1p(abs(x))`` so the
    selected branch keeps unit slope at exactly zero.
    """

    return torch.where(x >= 0, torch.log1p(x), -torch.log1p(-x))


def allocate_species_sizes(hidden_dim: int, ratios: Sequence[int]) -> tuple[int, int, int]:
    """Allocate ``hidden_dim`` coordinates according to three non-negative ratios."""

    if hidden_dim <= 0:
        raise ValueError("hidden_dim must be positive")
    if len(ratios) != 3:
        raise ValueError("ratios must contain exactly three values")
    if any(ratio < 0 for ratio in ratios):
        raise ValueError("ratios must be non-negative")
    total = sum(ratios)
    if total <= 0:
        raise ValueError("at least one species ratio must be positive")

    positive = [index for index, ratio in enumerate(ratios) if ratio > 0]
    if hidden_dim < len(positive):
        raise ValueError("hidden_dim is too small to allocate every active species")

    sizes = [0, 0, 0]
    for index in positive:
        sizes[index] = 1

    remaining = hidden_dim - len(positive)
    if remaining:
        raw = [remaining * ratio / total for ratio in ratios]
        floors = [int(value) for value in raw]
        sizes = [size + floor for size, floor in zip(sizes, floors, strict=True)]
        leftover = hidden_dim - sum(sizes)
        order = sorted(range(3), key=lambda index: raw[index] - floors[index], reverse=True)
        for index in order[:leftover]:
            sizes[index] += 1

    return sizes[0], sizes[1], sizes[2]


class NGTriSpeciesMLP(nn.Module):
    r"""Three-species heterogeneous MLP block.

    The candidate name is ``NG-TriSpecies-1:2:3``. Its stated population is
    50% species A, roughly 33% species B, and roughly 17% species C, which is
    represented by the default A:B:C ratio ``3:2:1``.

    The implementation omits unused slices of the three conceptual full
    projections. This is algebraically equivalent to computing full
    ``p0``, ``p1``, and ``p2`` tensors and then discarding the unused parts,
    while matching the parameter budget of a same-width SwiGLU/GEGLU block.
    """

    def __init__(
        self,
        input_dim: int,
        hidden_dim: int,
        output_dim: int,
        ratios: Sequence[int] = (3, 2, 1),
        bias: bool = True,
    ) -> None:
        super().__init__()
        self.input_dim = int(input_dim)
        self.hidden_dim = int(hidden_dim)
        self.output_dim = int(output_dim)
        self.ratios = tuple(int(value) for value in ratios)
        self.size_a, self.size_b, self.size_c = allocate_species_sizes(
            self.hidden_dim, self.ratios
        )

        self.proj0 = nn.Linear(self.input_dim, self.hidden_dim, bias=bias)
        self.proj1_a = (
            nn.Linear(self.input_dim, self.size_a, bias=bias) if self.size_a else None
        )
        size_p2 = self.size_b + self.size_c
        self.proj2_bc = nn.Linear(self.input_dim, size_p2, bias=bias) if size_p2 else None
        self.down = nn.Linear(self.hidden_dim, self.output_dim, bias=bias)

    @property
    def species_sizes(self) -> tuple[int, int, int]:
        """Return the number of A, B, and C coordinates."""

        return self.size_a, self.size_b, self.size_c

    def species_features(self, x: Tensor) -> tuple[Tensor, Tensor, Tensor]:
        """Return the three species outputs before concatenation."""

        p0 = self.proj0(x)
        empty = p0[..., :0]

        if self.size_a:
            if self.proj1_a is None:
                raise RuntimeError("species A projection was not initialized")
            p1_a = self.proj1_a(x)
            phi_a = signed_log1p(torch.minimum(p0[..., : self.size_a], p1_a))
        else:
            phi_a = empty

        if self.size_b or self.size_c:
            if self.proj2_bc is None:
                raise RuntimeError("species B/C projection was not initialized")
            p2_bc = self.proj2_bc(x)
        else:
            p2_bc = empty

        start_b = self.size_a
        end_b = start_b + self.size_b
        if self.size_b:
            phi_b = torch.minimum(p0[..., start_b:end_b], p2_bc[..., : self.size_b])
        else:
            phi_b = empty

        if self.size_c:
            p0_c = p0[..., end_b:]
            p2_c = p2_bc[..., self.size_b :]
            phi_c = p2_c / (1.0 + p0_c.abs())
        else:
            phi_c = empty

        return phi_a, phi_b, phi_c

    def forward(self, x: Tensor) -> Tensor:
        phi_a, phi_b, phi_c = self.species_features(x)
        hidden = torch.cat((phi_a, phi_b, phi_c), dim=-1)
        return self.down(hidden)
