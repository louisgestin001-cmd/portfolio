"""Fast structural diagnostics that run in CI without model training."""

from __future__ import annotations

import torch

from ng_cell_lab import NGEnergyMax1, NGEnergyMax2, NGLagMean1, NGStateMinU1


def statemin_period_two() -> float:
    cell = NGStateMinU1()
    x = torch.full((2048, 1), -1.0)
    state0 = torch.empty_like(x).uniform_(-0.9, 0.9)
    _, state1 = cell(x, state0)
    _, state2 = cell(x, state1)
    return float((state2 - state0).abs().max())


def energymax1_forgets_after_one_step() -> float:
    torch.manual_seed(0)
    cell = NGEnergyMax1()
    state = torch.randn(512, 16)
    x1 = torch.randn_like(state)
    x2 = torch.randn_like(state)
    _, state1 = cell(x1, state)
    y_a, _ = cell(x2, state1)
    _, state1_b = cell(x1, torch.randn_like(state))
    y_b, _ = cell(x2, state1_b)
    return float((y_a - y_b).abs().max())


def lagmean_centering_collapse() -> float:
    torch.manual_seed(1)
    cell = NGLagMean1()
    x = torch.randn(1024, 128)
    x = x - x.mean(dim=-1, keepdim=True)
    _, state = cell(x, cell.initial_state(x))
    return float(state.std())


def energymax2_is_bounded_by_input_scale() -> float:
    torch.manual_seed(2)
    cell = NGEnergyMax2(rho=0.999)
    x = torch.randn(1024, 128) * 8.0
    y, _ = cell(x, cell.initial_state(x))
    return float(y.abs().quantile(0.99))


def main() -> None:
    results = {
        "StateMin max two-cycle error": statemin_period_two(),
        "EnergyMax-1 prehistory influence after overwrite": energymax1_forgets_after_one_step(),
        "LagMean centered-state std": lagmean_centering_collapse(),
        "EnergyMax-2 p99 |y| at sigma=8": energymax2_is_bounded_by_input_scale(),
    }
    for name, value in results.items():
        print(f"{name}: {value:.8g}")

    assert results["StateMin max two-cycle error"] < 1e-6
    assert results["EnergyMax-1 prehistory influence after overwrite"] == 0.0
    assert results["LagMean centered-state std"] < 1e-6
    assert results["EnergyMax-2 p99 |y| at sigma=8"] < 25.0


if __name__ == "__main__":
    main()
