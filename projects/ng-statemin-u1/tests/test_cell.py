from __future__ import annotations

import pytest
import torch

from ng_statemin import NGStateMinU1Layer, ng_state_min_u1


def test_closed_form_equivalence() -> None:
    torch.manual_seed(0)
    x = torch.randn(2048, dtype=torch.float64)
    state = torch.randn(2048, dtype=torch.float64)
    direct = ng_state_min_u1(x, state)
    closed = (-state - torch.abs(2 * x - state)) / 2
    torch.testing.assert_close(direct, closed, rtol=0.0, atol=1e-12)


def test_period_two_involution_on_memory_branch() -> None:
    # For b < 0 and states in [2b, 0], the first branch is selected and
    # T_b(s) = b - s. Therefore T_b(T_b(s)) = s exactly.
    b = torch.full((1024,), -1.0, dtype=torch.float64)
    state = torch.linspace(-2.0, 0.0, 1024, dtype=torch.float64)
    state_1 = ng_state_min_u1(b, state)
    state_2 = ng_state_min_u1(b, state_1)
    torch.testing.assert_close(state_2, state, rtol=0.0, atol=1e-12)


def test_temporal_derivative_is_minus_one_or_zero_off_boundary() -> None:
    x = torch.tensor([-2.0, 2.0], requires_grad=False)
    state = torch.tensor([-1.0, -1.0], requires_grad=True)
    out = ng_state_min_u1(x, state)
    out.sum().backward()
    assert state.grad is not None
    assert set(state.grad.tolist()).issubset({-1.0, 0.0})


def test_layer_shapes_and_backward() -> None:
    layer = NGStateMinU1Layer(input_size=3, hidden_size=7)
    sequence = torch.randn(5, 11, 3, requires_grad=True)
    outputs, final_state = layer(sequence)
    assert outputs.shape == (5, 11, 7)
    assert final_state.shape == (5, 7)
    outputs.square().mean().backward()
    assert sequence.grad is not None
    assert torch.isfinite(sequence.grad).all()


def test_shape_mismatch_is_rejected() -> None:
    with pytest.raises(ValueError):
        ng_state_min_u1(torch.zeros(2, 3), torch.zeros(2, 4))
