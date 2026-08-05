# Research roadmap

## Milestone 1 — Unified benchmark runner

Create one runner with:

- identical train/validation/test splits;
- equal hidden widths and parameter-matched alternatives;
- identical optimizer, step budget, gradient clipping, and early stopping;
- at least 10 random seeds;
- fixed-delay and variable-delay testing;
- out-of-distribution lengths;
- wall-clock and memory measurements on CPU and GPU.

## Milestone 2 — Standard task suite

- copy memory;
- adding problem;
- associative recall;
- parity and phase-sensitive controls;
- sequential and permuted MNIST/digits;
- event streams with overwrite;
- synthetic audio/video transients;
- tasks with mean-zero and normalized hidden states.

## Milestone 3 — Derived candidates

### StateMin-U2

Add a phase-invariant readout or two-phase state while retaining the non-attenuating branch.

### ShiftCompare-U2

Constrain the sign of the temporal Jacobian or explicitly demodulate the period-two phase.

### EnergyMax-3

Use a soft max-absolute selector during training and an optionally hardened selector at inference. Compare straight-through and temperature-annealed variants.

### LagProj-K

Replace the single mean with a small bank of K projections or non-centered statistics. Test K in {2, 4, 8} while measuring cross-time rank and cost.

## Milestone 4 — Novelty audit

Perform a systematic literature search covering:

- min/max-plus and tropical recurrent networks;
- piecewise-linear RNN dynamics;
- multiplicative integration and second-order RNNs;
- max-based and event-based memory;
- global-context and squeeze/excitation modulation;
- low-rank recurrent state summaries.

Only after this audit should any exact novelty claim be made.
