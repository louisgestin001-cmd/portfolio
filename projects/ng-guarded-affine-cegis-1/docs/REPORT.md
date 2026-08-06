# NG-GuardedAffine-CEGIS-1 — experimental report

## Verdict

The system recovers a guarded integer piecewise-affine protocol from mixed black-box outputs, including saturations, a non-invertible reset, a guarded send, an acknowledgement reset and a three-region timeout/fast-retransmit rule.

This is a strong research prototype, not a demonstrated major discovery.

## Hidden protocol

The state is

\[
(c,r,e),\qquad 0\le c\le7,\quad0\le r\le3,\quad e\in\mathbb Z.
\]

The observed five-dimensional output is a random dense linear mixing of this state plus a bias.

The action set contains six coordinate probes and four protocol actions:

- `send`: if credit is positive, decrement credit and increment epoch;
- `ack`: saturating credit increment and retry reset;
- `timeout`: no-op without outstanding work, retry increment below the retry limit, and fast retransmit at the limit;
- `reset`: constant singular map to the reset state.

## Exact result

On seed 0:

- latent dimension: 3;
- bounded coordinate ranges recovered: credit relative range \([-4,3]\), retry relative range \([-1,2]\);
- unbounded coordinate recovered: epoch;
- counterexamples needed to refine guards: 8;
- exhaustive transition agreement on the verification grid: 100%;
- random trace agreement at length 500: 100%;
- bounded-state safety proof: passed;
- certificate: accepted.

Rule complexity:

| Action | Tree depth | Affine regions |
|---|---:|---:|
| `tick`, `untick`, `reset` | 0 | 1 |
| saturating coordinate actions | 1 | 2 |
| `send` | 1 | 2 |
| `ack` | 1 | 2 |
| `timeout` | 2 | 3 |

The learned complexity matches the actual control structure.

## Why multi-step basis validation matters

At the initial state, `timeout` changes the retry counter exactly like `retry_up`. A one-step method can therefore incorrectly choose `timeout/retry_down` as a coordinate pair.

The corrected compiler checks that repeated applications remain on a one-dimensional response ray. `retry_up` reaches a plateau on that ray; `timeout` eventually leaves it because fast retransmit also changes epoch. This removes the false basis.

## Noise stress test

Five random output mixtures per noise level:

| Output noise standard deviation | Accepted |
|---:|---:|
| 0 | 5/5 |
| 0.0001 | 5/5 |
| 0.001 | 5/5 |
| 0.003 | 5/5 |
| 0.01 | 5/5 |
| 0.03 | 3/5 |
| 0.10 | 0/5 |

Up to 1% noise, all 25 tested cases recover exact grid transitions, exact long-trace states and the safety certificate. At 3%, failures are rejected because the basis dimension or long-trace agreement is insufficient. At 10%, no translation basis is accepted.

## Length 100,000

A random trace of 100,000 actions was executed by both the original protocol and the compiled program. Final state agreement was exact.

The current Python tree interpreter was slower than the direct handwritten protocol, so this is a correctness result, not a speed result. Code generation or rule fusion would be required for performance.

## Query accounting

The seed-0 certificate used 3,916 unique black-box word queries, including:

- structural basis and bound probes;
- exhaustive bounded-grid transition validation;
- readout calibration;
- 500 long validation traces.

Only eight returned states became guard-refinement counterexamples. Most queries are certification cost, not discovery cost.

## Neural limitation

A preliminary normalized GRU reached approximately 92.6% exact decoded-state agreement on random traces up to length 80. That was not reliable enough for strict integer rounding and pure-neural piecewise compilation. The current accepted results therefore use exact or deterministically noisy protocol outputs, not an accepted extraction from that GRU.

This negative result is important: a formal certificate must reject a network whose local state geometry has not crystallized sufficiently.

## Scientific status

The potentially useful contribution is the combination of:

\[
\text{mixed-output coordinate discovery}
+
\text{singular affine finite differences}
+
\text{counterexample-guided guards}
+
\text{integer rounding}
+
\text{exhaustive safety certification}.
\]

The benchmark remains synthetic and exposes coordinate probe actions. Direct comparisons with active register-automata learners and black-box piecewise-affine abstraction methods are still required.

## Randomized capacities and guard thresholds

The structural compiler was also tested on 20 exact protocol instances with independently varied credit capacities from 4 to 10 and retry limits from 2 to 5.

\[
\boxed{20/20\text{ accepted}}
\]

A second suite varied capacities, limits, output mixtures and noise levels up to 1%:

\[
\boxed{10/10\text{ accepted}}.
\]

This exposed and fixed another false-basis failure: when the retry limit is high, `timeout` can follow the retry direction for several steps before fast retransmit changes epoch. Basis validation now probes repeatedly until the candidate plateaus or leaves its response ray, rather than checking only two or three applications.
