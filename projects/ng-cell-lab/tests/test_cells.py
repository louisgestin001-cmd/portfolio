from __future__ import annotations

import math

import pytest
import torch

from ng_cell_lab import (
    NGEnergyMax1,
    NGEnergyMax2,
    NGLagMean1,
    NGSequenceLayer,
    NGShiftCompareMul,
    NGStateMinU1,
    make_cell,
)


def test_statemin_exact_law() -> None:
    x = torch.tensor([[1.0, -2.0]])
    state = torch.tensor([[0.25, 0.5]])
    y, next_state = NGStateMinU1()(x, state)
    expected = torch.minimum(x - state, -x)
    torch.testing.assert_close(y, expected)
    torch.testing.assert_close(next_state, expected)


def test_statemin_two_cycle_on_memory_branch() -> None:
    cell = NGStateMinU1()
    x = torch.tensor([[-1.0]])
    state0 = torch.tensor([[-0.2]])
    _, state1 = cell(x, state0)
    _, state2 = cell(x, state1)
    torch.testing.assert_close(state2, state0)


def test_shiftcompare_constant_and_clip() -> None:
    cell = NGShiftCompareMul(clip=2.0)
    assert cell.shift == pytest.approx(1.231609 * math.sin(1.0) + 0.029583)
    x = torch.full((4, 8), 1_000.0)
    state = torch.zeros_like(x)
    y, next_state = cell(x, state)
    assert torch.isfinite(y).all()
    assert y.abs().max().item() <= 2.0
    torch.testing.assert_close(y, next_state)


def test_energymax1_overwrites_state_with_current_input() -> None:
    cell = NGEnergyMax1()
    x = torch.tensor([[1.0, -2.0, 0.5]])
    state = torch.tensor([[9.0, 9.0, 9.0]])
    _, next_state = cell(x, state)
    torch.testing.assert_close(next_state, x)


def test_energymax2_gate_is_bounded_and_sign_is_preserved() -> None:
    cell = NGEnergyMax2(rho=0.999)
    x = torch.tensor([[2.0, -3.0]])
    state = torch.zeros_like(x)
    y, next_state = cell(x, state)
    assert torch.sign(next_state[0, 0]) == 1
    assert torch.sign(next_state[0, 1]) == -1
    energy = x.abs().mean(dim=-1, keepdim=True)
    gate = energy / (1.0 + energy)
    assert 0.0 < gate.item() < 1.0
    torch.testing.assert_close(y, 0.922865 * next_state)


def test_energymax2_rejects_invalid_rho() -> None:
    with pytest.raises(ValueError):
        NGEnergyMax2(rho=1.1)


def test_lagmean_exact_step_and_scalar_state() -> None:
    cell = NGLagMean1()
    x = torch.tensor([[1.0, 3.0]])
    state = torch.tensor([[2.0]])
    y, next_state = cell(x, state)
    expected_state = torch.tensor([[0.5 * 2.0 + 0.011376]])
    expected_y = torch.tensor([[1.902186, 5.902186]])
    torch.testing.assert_close(next_state, expected_state)
    torch.testing.assert_close(y, expected_y)
    assert next_state.shape == (1, 1)


def test_lagmean_collapses_after_centering() -> None:
    cell = NGLagMean1()
    x = torch.randn(64, 32)
    x = x - x.mean(dim=-1, keepdim=True)
    state = cell.initial_state(x)
    _, next_state = cell(x, state)
    torch.testing.assert_close(next_state, torch.full_like(next_state, 0.011376), atol=1e-6, rtol=0)


def test_sequence_layer_shapes_for_vector_and_scalar_state() -> None:
    sequence = torch.randn(3, 5, 7)
    outputs, vector_state = NGSequenceLayer(NGEnergyMax2())(sequence)
    assert outputs.shape == (3, 5, 7)
    assert vector_state.shape == (3, 7)

    outputs, scalar_state = NGSequenceLayer(NGLagMean1())(sequence)
    assert outputs.shape == (3, 5, 7)
    assert scalar_state.shape == (3, 1)


def test_registry_constructs_cells() -> None:
    assert isinstance(make_cell("NG-StateMin-U1"), NGStateMinU1)
    with pytest.raises(KeyError):
        make_cell("unknown")
