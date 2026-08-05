# Experimental results

## Reading these results correctly

These are preliminary experiments, not a single standardized leaderboard. Rows are directly comparable only inside the same protocol. The normalized source table is [`results/experimental_summary.csv`](../results/experimental_summary.csv).

## Selected findings

### Fixed-delay noisy memory

| Cell | Result | Important interpretation |
|---|---:|---|
| NG-StateMin-U1 | 99.97% at length 40 | collapses/inverts on odd lengths because the memory is phase-two |
| NG-ShiftCompare-Mul | 99.97% at length 40 | also nearly perfectly reverses phase on odd lengths |
| NG-EnergyMax-1 | approximately 50% beyond one-step delay | exact structural limitation |
| NG-EnergyMax-2, rho=0.99 | 99.93% at 40; 95.17% at 80 | no parity pathology; decay limits long extrapolation |
| NG-LagMean-1 | 100% at one-step recall; approximately 50% after two steps | exact one-step state summary |

### Sequential 8x8 digits

| Model or cell | Accuracy | Protocol note |
|---|---:|---|
| NG-StateMin-U1 | 25.33% | 3 seeds, original StateMin protocol |
| NG-ShiftCompare-Mul | 42.74% | 3 seeds, same family of scalar-state benchmark |
| NG-EnergyMax-2 | 9.85% | quick hard-selection experiment |
| NG-LagMean-1 | 21.41% | 3 seeds, separate quick protocol |
| U1-Tanh | 35.78% | StateMin protocol |
| Elman-Tanh | 84.59% | StateMin protocol |
| GRU | 61.33% | LagMean quick protocol, one seed |

Do not compare the last two baseline values as though they came from identical training schedules.

### Adding two marked values

| Cell or model | MAE lower is better |
|---|---:|
| NG-StateMin-U1 | 0.3189 |
| NG-ShiftCompare-Mul | approximately 0.3233 |
| NG-EnergyMax-1 | 0.3341 |
| NG-EnergyMax-2 | **0.1918** |
| GRU quick baseline | 0.0664 |

EnergyMax-2 materially improves over EnergyMax-1, but remains far from the trained GRU baseline.

## Structural tests more important than headline accuracy

- **StateMin and ShiftCompare:** test both odd and even lengths. A fixed even delay hides their phase code.
- **EnergyMax-1:** test more than one blank/noisy step. Its state is overwritten by the current input.
- **EnergyMax-2:** test replacement of an old event, not only preservation. Setting rho to exactly one can freeze historical extrema.
- **LagMean:** test mean-zero patterns and LayerNorm. Standard random data can hide the rank-one bottleneck.

## Reproduction status

The common package and structural tests are reproducible through CI. The training results were produced during separate exploratory runs with different schedules. A unified fair runner is the next research milestone.
