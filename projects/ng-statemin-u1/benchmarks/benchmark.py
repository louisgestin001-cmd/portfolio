"""Reproducible compact benchmark suite for NG-StateMin-U1.

Example:
    python benchmarks/benchmark.py --task delayed_noise --models NG-StateMin-U1 U1-ReLU
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import random
import time
from pathlib import Path
from typing import Callable

os.environ.setdefault("OMP_NUM_THREADS", "4")
os.environ.setdefault("MKL_NUM_THREADS", "4")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "4")

import numpy as np
import torch
from torch import Tensor, nn

from ng_statemin import ng_state_min_u1

torch.set_num_threads(4)
torch.set_num_interop_threads(1)


class ScalarStateNet(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int) -> None:
        super().__init__()
        self.hidden_dim = hidden_dim
        self.inp = nn.Linear(input_dim, hidden_dim)
        self.head = nn.Linear(hidden_dim, output_dim)

    def cell(self, preactivation: Tensor, state: Tensor) -> Tensor:
        raise NotImplementedError

    def forward(self, x: Tensor) -> Tensor:
        state = x.new_zeros(x.size(0), self.hidden_dim)
        for x_t in x.unbind(dim=1):
            state = self.cell(self.inp(x_t), state)
        return self.head(state)


class NGStateMinNet(ScalarStateNet):
    def cell(self, preactivation: Tensor, state: Tensor) -> Tensor:
        return ng_state_min_u1(preactivation, state)


class U1ReLU(ScalarStateNet):
    def cell(self, preactivation: Tensor, state: Tensor) -> Tensor:
        return torch.relu(preactivation + state)


class U1Tanh(ScalarStateNet):
    def cell(self, preactivation: Tensor, state: Tensor) -> Tensor:
        return torch.tanh(preactivation + state)


class ElmanNet(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int, activation: str) -> None:
        super().__init__()
        self.rnn = nn.RNN(
            input_dim, hidden_dim, batch_first=True, nonlinearity=activation
        )
        self.head = nn.Linear(hidden_dim, output_dim)
        with torch.no_grad():
            nn.init.orthogonal_(self.rnn.weight_hh_l0)

    def forward(self, x: Tensor) -> Tensor:
        outputs, _ = self.rnn(x)
        return self.head(outputs[:, -1])


class GRUNet(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int) -> None:
        super().__init__()
        self.gru = nn.GRU(input_dim, hidden_dim, batch_first=True)
        self.head = nn.Linear(hidden_dim, output_dim)

    def forward(self, x: Tensor) -> Tensor:
        outputs, _ = self.gru(x)
        return self.head(outputs[:, -1])


MODELS: dict[str, Callable[[int, int, int], nn.Module]] = {
    "NG-StateMin-U1": NGStateMinNet,
    "U1-ReLU": U1ReLU,
    "U1-Tanh": U1Tanh,
    "Elman-ReLU": lambda i, h, o: ElmanNet(i, h, o, "relu"),
    "Elman-Tanh": lambda i, h, o: ElmanNet(i, h, o, "tanh"),
    "GRU": GRUNet,
}


def seed_all(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def delayed_blank(batch: int, seq: int = 40) -> tuple[Tensor, Tensor]:
    bits = torch.randint(0, 2, (batch,))
    x = torch.zeros(batch, seq, 2)
    x[:, 0, 0] = bits.float() * 2 - 1
    x[:, 0, 1] = 1.0
    return x, bits


def delayed_noise(batch: int, seq: int = 40) -> tuple[Tensor, Tensor]:
    bits = torch.randint(0, 2, (batch,))
    x = torch.randn(batch, seq, 2) * 0.20
    x[:, 0, 0] = bits.float() * 2 - 1
    x[:, 0, 1] = 1.0
    x[:, 1:, 1] = 0.0
    return x, bits


def adding(batch: int, seq: int = 40) -> tuple[Tensor, Tensor]:
    values = torch.rand(batch, seq)
    marks = torch.zeros(batch, seq)
    first = torch.randint(0, seq // 2, (batch,))
    second = torch.randint(seq // 2, seq, (batch,))
    rows = torch.arange(batch)
    marks[rows, first] = 1.0
    marks[rows, second] = 1.0
    x = torch.stack([values, marks], dim=-1)
    y = (values[rows, first] + values[rows, second]).unsqueeze(1)
    return x, y


TASKS: dict[str, tuple[Callable[[int], tuple[Tensor, Tensor]], str]] = {
    "delayed_blank": (delayed_blank, "classification"),
    "delayed_noise": (delayed_noise, "classification"),
    "adding": (adding, "regression"),
}


def evaluate(
    model: nn.Module,
    generator: Callable[[int], tuple[Tensor, Tensor]],
    task_kind: str,
    *,
    batches: int = 8,
    batch_size: int = 256,
) -> tuple[float, float]:
    criterion: nn.Module = (
        nn.CrossEntropyLoss() if task_kind == "classification" else nn.MSELoss()
    )
    model.eval()
    total_loss = 0.0
    total_metric = 0.0
    count = 0
    with torch.no_grad():
        for _ in range(batches):
            x, y = generator(batch_size)
            prediction = model(x)
            total_loss += float(criterion(prediction, y)) * batch_size
            if task_kind == "classification":
                total_metric += float((prediction.argmax(-1) == y).sum())
            else:
                total_metric += float((prediction - y).abs().sum())
            count += batch_size
    return total_loss / count, total_metric / count


def train_one(
    model_name: str,
    task_name: str,
    seed: int,
    *,
    steps: int,
    hidden: int,
    batch_size: int,
    learning_rate: float,
) -> dict[str, float | int | str]:
    seed_all(seed)
    generator, task_kind = TASKS[task_name]
    output_dim = 2 if task_kind == "classification" else 1
    model = MODELS[model_name](2, hidden, output_dim)
    criterion: nn.Module = (
        nn.CrossEntropyLoss() if task_kind == "classification" else nn.MSELoss()
    )
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=learning_rate, weight_decay=1e-4
    )

    start = time.perf_counter()
    for _ in range(steps):
        model.train()
        x, y = generator(batch_size)
        prediction = model(x)
        loss = criterion(prediction, y)
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
        optimizer.step()

    test_loss, metric = evaluate(model, generator, task_kind)
    return {
        "task": task_name,
        "model": model_name,
        "seed": seed,
        "params": sum(parameter.numel() for parameter in model.parameters()),
        "test_loss": test_loss,
        "accuracy" if task_kind == "classification" else "mae": metric,
        "seconds": time.perf_counter() - start,
    }


def write_rows(path: Path, rows: list[dict[str, float | int | str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() == ".json":
        path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
        return
    fieldnames = sorted({key for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", choices=TASKS, required=True)
    parser.add_argument("--steps", type=int, default=700)
    parser.add_argument("--seeds", type=int, default=3)
    parser.add_argument("--hidden", type=int, default=24)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--learning-rate", type=float, default=3e-3)
    parser.add_argument("--models", nargs="+", choices=MODELS, default=list(MODELS))
    parser.add_argument("--out", type=Path, default=Path("results/run.json"))
    args = parser.parse_args()

    rows: list[dict[str, float | int | str]] = []
    for model_name in args.models:
        for seed in range(args.seeds):
            row = train_one(
                model_name,
                args.task,
                seed,
                steps=args.steps,
                hidden=args.hidden,
                batch_size=args.batch_size,
                learning_rate=args.learning_rate,
            )
            rows.append(row)
            print(json.dumps(row), flush=True)
    write_rows(args.out, rows)


if __name__ == "__main__":
    main()
