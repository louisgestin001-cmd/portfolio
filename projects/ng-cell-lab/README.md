# NG Cell Lab

[![NG Cell Lab CI](https://github.com/louisgestin001-cmd/portfolio/actions/workflows/ng-cell-lab-ci.yml/badge.svg)](https://github.com/louisgestin001-cmd/portfolio/actions/workflows/ng-cell-lab-ci.yml)

**NG Cell Lab** is a reproducible research zoo for compact recurrent and collectively modulated neural-cell laws.

The project currently contains five cells:

1. **NG-StateMin-U1** — a minimal piecewise-linear period-two memory;
2. **NG-ShiftCompare-Mul** — a shifted multiplicative recurrent comparator;
3. **NG-EnergyMax-1** — a global-energy-modulated two-frame operator;
4. **NG-EnergyMax-2** — a derived sparse event/extremum memory;
5. **NG-LagMean-1** — a rank-one delayed collective modulator.

The goal is not to rename ordinary RNNs. Each law is implemented exactly, tested structurally, benchmarked against useful baselines, and documented with both positive results and failure modes.

> **Research status:** preliminary. The repository does not claim established literature-level novelty, state-of-the-art performance, or that these cells replace RNN, GRU, LSTM, SSM, or attention architectures.

## Installation

```bash
cd projects/ng-cell-lab
python -m pip install -e ".[test]"
pytest -q
python benchmarks/diagnostics.py
```

## Common API

```python
import torch
from ng_cell_lab import NGEnergyMax2, NGSequenceLayer

x = torch.randn(8, 100, 64)  # batch, time, hidden
layer = NGSequenceLayer(NGEnergyMax2(rho=0.999))
y, final_state = layer(x)

print(y.shape)           # [8, 100, 64]
print(final_state.shape) # [8, 64]
```

Every cell follows:

```python
y_t, s_t = cell(x_t, s_previous)
```

`NGLagMean1` is the exception in state shape: it stores one scalar per sample while emitting a full hidden vector.

## Cell overview

| Cell | State | Main mechanism | Strongest observed use | Principal failure |
|---|---|---|---|---|
| NG-StateMin-U1 | vector | `min(x-s, -x)` | tiny exact period-two memory | odd/even phase inversion |
| NG-ShiftCompare-Mul | vector | shifted `tanh` comparator × input branch | richer scalar recurrence; 42.7% sequential digits | phase-two attractor; costly |
| NG-EnergyMax-1 | previous input vector | mean absolute energy × current input, then `max` | one-step transient comparison | no memory beyond one step; quadratic scaling |
| NG-EnergyMax-2 | vector | bounded energy gate + max-absolute event memory | long sparse event memory without parity failure | poor ordered dense-sequence representation |
| NG-LagMean-1 | scalar | previous layer mean × current coordinates | two-frame multiplicative/XOR-like modulation | rank-one, one-step, LayerNorm collapse |

See [Cell cards](docs/CELLS.md) for equations and mathematical diagnostics, and [Results](docs/RESULTS.md) for the experimental evidence.

## Important findings

### 1. Easy memory benchmarks can be deceptive

StateMin and ShiftCompare both reached almost perfect accuracy at a fixed even delay. Testing the same trained model at odd lengths revealed near-perfect class inversion. Their success came from a period-two phase code rather than a time-invariant memory.

### 2. A one-step operator can still be useful

EnergyMax-1 and LagMean-1 cannot propagate arbitrary information beyond one step. They nevertheless implement useful two-frame interactions: global energy comparison and delayed bilinear modulation.

### 3. EnergyMax-2 is the strongest memory primitive so far

The derived EnergyMax-2 variant removes the quadratic energy growth, preserves sign, avoids the odd/even pathology, and can retain sparse events over hundreds of steps when `rho` is close to one. It does not encode the order of many dense events well.

### 4. Collective summaries create severe information bottlenecks

LagMean transmits only the mean direction. Its cross-time Jacobian has rank at most one, it is blind to mean-zero patterns, and ordinary LayerNorm makes its dynamic state almost constant.

## Repository structure

```text
ng-cell-lab/
├── src/ng_cell_lab/
│   ├── cells.py          # exact candidate laws
│   ├── sequence.py       # batch-first scan wrapper
│   └── registry.py       # searchable cell metadata
├── tests/                # algebraic and structural tests
├── benchmarks/           # fast CI diagnostics
├── results/              # normalized result table
├── docs/                 # equations, findings, protocol caveats, roadmap
├── AI_USE_STATEMENT.md
├── CITATION.cff
├── LICENSE
└── pyproject.toml
```

## Reproducibility and comparison warning

The result table combines several preliminary experiments conducted at different stages. A row is only directly comparable with rows sharing the same `protocol_id`. The normalized table records the number of seeds, metric, task, and setting to prevent accidental apples-to-oranges claims.

For a publication-quality comparison, the next milestone is a unified runner with identical widths, parameter budgets, optimization schedules, data splits, and at least 10 seeds per task.

## Cell provenance

- **User-supplied candidates:** NG-StateMin-U1, NG-ShiftCompare-Mul, NG-EnergyMax-1, NG-LagMean-1.
- **Derived variant:** NG-EnergyMax-2 was proposed after diagnosing EnergyMax-1's one-step memory and quadratic amplitude growth.

The [AI-use statement](AI_USE_STATEMENT.md) describes the role of AI assistance.

## License

Code is released under the [MIT License](LICENSE). Experimental numbers and scientific claims should be cited with the exact repository commit because protocols may evolve.
