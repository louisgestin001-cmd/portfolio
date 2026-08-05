from __future__ import annotations

import pytest
import torch

from ng_cell_lab import NGTriSpeciesMLP, allocate_species_sizes, signed_log1p


def parameter_count(module: torch.nn.Module) -> int:
    return sum(parameter.numel() for parameter in module.parameters())


def test_default_species_allocation_matches_stated_population() -> None:
    assert allocate_species_sizes(64, (3, 2, 1)) == (32, 21, 11)


def test_allocation_rejects_invalid_ratios() -> None:
    with pytest.raises(ValueError):
        allocate_species_sizes(8, (0, 0, 0))
    with pytest.raises(ValueError):
        allocate_species_sizes(2, (1, 1, 1))


def test_signed_log1p_is_odd_and_finite_at_zero() -> None:
    x = torch.tensor([-3.0, -0.0, 0.0, 3.0], requires_grad=True)
    y = signed_log1p(x)
    torch.testing.assert_close(y[0], -y[-1])
    assert torch.isfinite(y).all()
    y.sum().backward()
    assert torch.isfinite(x.grad).all()


def test_trispecies_shapes_and_finite_gradients() -> None:
    block = NGTriSpeciesMLP(64, 64, 10)
    x = torch.randn(16, 64, requires_grad=True)
    output = block(x)
    assert output.shape == (16, 10)
    loss = output.square().mean()
    loss.backward()
    assert torch.isfinite(output).all()
    assert x.grad is not None
    assert torch.isfinite(x.grad).all()


def test_species_features_have_expected_widths() -> None:
    block = NGTriSpeciesMLP(12, 17, 5)
    phi_a, phi_b, phi_c = block.species_features(torch.randn(4, 12))
    assert (phi_a.shape[-1], phi_b.shape[-1], phi_c.shape[-1]) == block.species_sizes
    assert sum(block.species_sizes) == 17


def test_parameter_count_matches_same_width_glu() -> None:
    block = NGTriSpeciesMLP(64, 64, 10)
    same_width_glu_parameters = 2 * (64 * 64 + 64) + (64 * 10 + 10)
    assert parameter_count(block) == same_width_glu_parameters == 8970


def test_single_species_ablations_are_supported() -> None:
    assert NGTriSpeciesMLP(8, 12, 4, ratios=(1, 0, 0)).species_sizes == (12, 0, 0)
    assert NGTriSpeciesMLP(8, 12, 4, ratios=(0, 1, 0)).species_sizes == (0, 12, 0)
    assert NGTriSpeciesMLP(8, 12, 4, ratios=(0, 0, 1)).species_sizes == (0, 0, 12)
