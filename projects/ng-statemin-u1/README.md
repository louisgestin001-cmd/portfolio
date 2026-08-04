# NG-StateMin-U1

[![CI](https://github.com/louisgestin001-cmd/portfolio/actions/workflows/ng-statemin-ci.yml/badge.svg)](https://github.com/louisgestin001-cmd/portfolio/actions/workflows/ng-statemin-ci.yml)

**NG-StateMin-U1** is an experimental, elementwise recurrent state law:

\[
\boxed{s_t = y_t = \min(x_t-s_{t-1}, -x_t)}.
\]

It uses one scalar state per hidden coordinate, no learned recurrent coefficient, two piecewise-linear branches, one subtraction, one negation, and one minimum operation.

## Status

This is a **preliminary research artifact**. The exact law and its observed behavior are worth studying, but this repository does not claim that NG-StateMin-U1 is state of the art, that it replaces standard recurrent cells, or that literature-level novelty has been established.

The most interesting verified behavior is an exact period-two memory regime. The most important failure is a strong odd/even length dependence.

## Main findings

- The temporal state derivative is exactly `-1` or `0` away from the branch boundary.
- A constant negative preactivation can produce an exact involution: two recurrent steps recover the previous state.
- On a 40-step one-bit memory task, the cell reached 100% accuracy with 122 parameters.
- Under moderate input noise, it reached 99.97% mean accuracy over three seeds.
- When trained only at length 40, it nearly inverted predictions at lengths 39 and 41.
- It did not outperform a standard dense tanh RNN on richer sequential classification.

See the full [experimental report](docs/REPORT.md) and [summary table](results/summary.csv).

## Installation

From this project directory:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
python -m pip install --upgrade pip
pip install -e ".[test]"
```

## Minimal use

```python
import torch
from ng_statemin import NGStateMinU1Layer

layer = NGStateMinU1Layer(input_size=8, hidden_size=32)
sequence = torch.randn(4, 100, 8)
outputs, final_state = layer(sequence)

print(outputs.shape)      # (4, 100, 32)
print(final_state.shape)  # (4, 32)
```

The bare transition is also exposed:

```python
from ng_statemin import ng_state_min_u1

next_state = ng_state_min_u1(preactivation, previous_state)
```

## Run tests

```bash
pytest
ruff check .
```

## Reproduce a compact benchmark

```bash
python benchmarks/benchmark.py \
  --task delayed_noise \
  --models NG-StateMin-U1 U1-ReLU U1-Tanh Elman-Tanh \
  --steps 700 \
  --seeds 3 \
  --out results/delayed_noise.json
```

Available tasks in the compact script are `delayed_blank`, `delayed_noise`, and `adding`.

## Repository layout

```text
ng-statemin-u1/
├── src/ng_statemin/       # reusable PyTorch implementation
├── tests/                 # algebraic and gradient tests
├── benchmarks/            # compact reproducible benchmarks
├── results/               # reported summary
├── docs/REPORT.md         # detailed interpretation and limitations
├── AI_USE_STATEMENT.md    # transparent AI-assistance disclosure
├── CITATION.cff
└── pyproject.toml
```

## Scientific caution

The current evidence supports the term **oscillatory memory primitive** more strongly than **general recurrent neuron**. A publishable follow-up should introduce and evaluate a phase-corrected U2 variant, use more seeds, include stronger baselines, and complete a systematic literature review.

## Citation

Citation metadata is available in [`CITATION.cff`](CITATION.cff). Until a paper or archived release exists, cite the repository and commit used.

## License

Code is released under the MIT License. Experimental claims, tables, and interpretations remain subject to correction as the project develops.
