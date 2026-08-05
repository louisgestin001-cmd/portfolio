"""Parameter-matched Digits benchmark for NG-TriSpecies-1:2:3.

Install benchmark dependencies first::

    pip install -e ".[benchmark]"

The default run evaluates five seeds, low-data training, Gaussian test noise,
and species-ratio ablations. Use ``--quick`` for a short smoke experiment.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import torch
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from torch import Tensor, nn
from torch.nn import functional as F

from ng_cell_lab import NGTriSpeciesMLP


@dataclass(frozen=True)
class Result:
    model: str
    protocol: str
    seed: int
    accuracy: float
    parameters: int


class ActivationMLP(nn.Module):
    def __init__(self, activation: Callable[[Tensor], Tensor], hidden_dim: int = 120) -> None:
        super().__init__()
        self.up = nn.Linear(64, hidden_dim)
        self.down = nn.Linear(hidden_dim, 10)
        self.activation = activation

    def forward(self, x: Tensor) -> Tensor:
        return self.down(self.activation(self.up(x)))


class GatedMLP(nn.Module):
    def __init__(self, gate: str, hidden_dim: int = 64) -> None:
        super().__init__()
        self.gate = gate
        self.proj_gate = nn.Linear(64, hidden_dim)
        self.proj_value = nn.Linear(64, hidden_dim)
        self.down = nn.Linear(hidden_dim, 10)

    def forward(self, x: Tensor) -> Tensor:
        preactivation = self.proj_gate(x)
        if self.gate == "swiglu":
            gate = F.silu(preactivation)
        elif self.gate == "geglu":
            gate = F.gelu(preactivation)
        else:
            raise ValueError(f"unknown gate: {self.gate}")
        return self.down(gate * self.proj_value(x))


def count_parameters(module: nn.Module) -> int:
    return sum(parameter.numel() for parameter in module.parameters())


def build_model(name: str) -> nn.Module:
    builders: dict[str, Callable[[], nn.Module]] = {
        "GELU": lambda: ActivationMLP(F.gelu),
        "ReLU": lambda: ActivationMLP(F.relu),
        "SwiGLU": lambda: GatedMLP("swiglu"),
        "GEGLU": lambda: GatedMLP("geglu"),
        "TriSpecies-3:2:1": lambda: NGTriSpeciesMLP(64, 64, 10, ratios=(3, 2, 1)),
        "TriSpecies-1:1:1": lambda: NGTriSpeciesMLP(64, 64, 10, ratios=(1, 1, 1)),
        "Species-A-only": lambda: NGTriSpeciesMLP(64, 64, 10, ratios=(1, 0, 0)),
        "Species-B-only": lambda: NGTriSpeciesMLP(64, 64, 10, ratios=(0, 1, 0)),
        "Species-C-only": lambda: NGTriSpeciesMLP(64, 64, 10, ratios=(0, 0, 1)),
    }
    try:
        return builders[name]()
    except KeyError as error:
        raise ValueError(f"unknown model: {name}") from error


def load_data() -> tuple[Tensor, Tensor, Tensor, Tensor]:
    features, labels = load_digits(return_X_y=True)
    features = features.astype(np.float32) / 16.0
    train_x, test_x, train_y, test_y = train_test_split(
        features,
        labels,
        test_size=0.25,
        random_state=123,
        stratify=labels,
    )
    scaler = StandardScaler().fit(train_x)
    train_x = scaler.transform(train_x).astype(np.float32)
    test_x = scaler.transform(test_x).astype(np.float32)
    return (
        torch.from_numpy(train_x),
        torch.from_numpy(train_y.astype(np.int64)),
        torch.from_numpy(test_x),
        torch.from_numpy(test_y.astype(np.int64)),
    )


def stratified_fraction(labels: Tensor, fraction: float, seed: int) -> Tensor:
    if fraction >= 1.0:
        return torch.arange(labels.numel())
    rng = np.random.default_rng(seed)
    labels_np = labels.numpy()
    selected: list[int] = []
    for label in range(10):
        candidates = np.flatnonzero(labels_np == label)
        amount = max(2, int(len(candidates) * fraction))
        selected.extend(rng.choice(candidates, amount, replace=False).tolist())
    return torch.tensor(selected, dtype=torch.long)


def train_one(
    model_name: str,
    seed: int,
    train_fraction: float,
    noise_std: float,
    epochs: int,
) -> Result:
    torch.manual_seed(seed)
    np.random.seed(seed)
    random.seed(seed)
    train_x, train_y, test_x, test_y = load_data()
    indices = stratified_fraction(train_y, train_fraction, seed)
    train_x = train_x[indices]
    train_y = train_y[indices]

    model = build_model(model_name)
    optimizer = torch.optim.AdamW(model.parameters(), lr=3e-3, weight_decay=1e-4)
    generator = torch.Generator().manual_seed(seed)
    batch_size = 128

    for _ in range(epochs):
        permutation = torch.randperm(train_x.shape[0], generator=generator)
        model.train()
        for start in range(0, train_x.shape[0], batch_size):
            batch = permutation[start : start + batch_size]
            optimizer.zero_grad(set_to_none=True)
            loss = F.cross_entropy(model(train_x[batch]), train_y[batch])
            loss.backward()
            optimizer.step()

    model.eval()
    with torch.no_grad():
        if noise_std:
            noise_generator = torch.Generator().manual_seed(seed + 10_000)
            test_x = test_x + noise_std * torch.randn(test_x.shape, generator=noise_generator)
        accuracy = float((model(test_x).argmax(dim=-1) == test_y).float().mean())

    protocol = f"fraction={train_fraction:g};noise={noise_std:g};epochs={epochs}"
    return Result(model_name, protocol, seed, accuracy, count_parameters(model))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("results/trispecies_rerun.csv"))
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()

    seeds = range(1 if args.quick else 5)
    epochs = 10 if args.quick else 70
    main_models = ["GELU", "ReLU", "SwiGLU", "GEGLU", "TriSpecies-3:2:1"]
    ablations = [
        "Species-A-only",
        "Species-B-only",
        "Species-C-only",
        "TriSpecies-1:1:1",
        "TriSpecies-3:2:1",
    ]

    results: list[Result] = []
    for model_name in main_models:
        for seed in seeds:
            results.append(train_one(model_name, seed, 1.0, 0.0, epochs))
            if not args.quick:
                results.append(train_one(model_name, seed, 0.2, 0.0, 100))
                for noise_std in (0.1, 0.2, 0.4):
                    results.append(train_one(model_name, seed, 1.0, noise_std, epochs))

    if not args.quick:
        for model_name in ablations:
            for seed in range(3):
                results.append(train_one(model_name, seed, 1.0, 0.0, epochs))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=Result.__dataclass_fields__.keys())
        writer.writeheader()
        writer.writerows(asdict(result) for result in results)

    print(json.dumps([asdict(result) for result in results], indent=2))


if __name__ == "__main__":
    main()
