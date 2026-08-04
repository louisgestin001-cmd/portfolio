# NG-StateMin-U1 — experimental report

## Candidate law

For each hidden coordinate,

\[
\boxed{s_t = y_t = \min(x_t-s_{t-1}, -x_t)}.
\]

Here, \(x_t\) is the current preactivation, \(s_{t-1}\) is the previous internal state, \(y_t\) is the emitted signal, and \(s_t\) is the next state.

This report records a preliminary experiment performed on 4 August 2026. It does **not** establish literature-level novelty or state-of-the-art performance.

## Exact algebraic properties

The law is equivalently

\[
s_t = \frac{-s_{t-1}-|2x_t-s_{t-1}|}{2}.
\]

Away from the branch boundary \(2x_t=s_{t-1}\), the temporal derivative is

\[
\frac{\partial s_t}{\partial s_{t-1}} \in \{-1,0\}.
\]

Thus the transition cannot produce an exploding temporal Jacobian. However, the reset branch erases the temporal gradient completely.

For a constant negative preactivation \(x_t=b<0\), states in the appropriate branch satisfy

\[
T_b(s)=b-s, \qquad T_b(T_b(s))=s.
\]

This is an exact period-two involution: memory can persist without attenuation, but its phase alternates every step.

## Experimental setup

The U1 comparisons use the same learned input projection and linear output head. Their scalar recurrent transitions are:

- NG-StateMin-U1: \(\min(x_t-s_{t-1},-x_t)\);
- U1-ReLU: \(\operatorname{ReLU}(x_t+s_{t-1})\);
- U1-Tanh: \(\tanh(x_t+s_{t-1})\).

The Elman RNN baselines use a learned dense recurrent matrix and therefore have more parameters.

## Results

### One-bit memory, 40-step delay

| Model | Parameters | Silence | Gaussian noise, sigma 0.20 |
|---|---:|---:|---:|
| NG-StateMin-U1 | 122 | 100.0% | 99.97% |
| U1-ReLU | 122 | 100.0% | 100.0% |
| U1-Tanh | 122 | 100.0% | 84.75% |
| Elman-Tanh | 722 | 100.0% | 100.0% |
| Elman-ReLU | 722 | 50.3% | unstable |

Means are over three seeds unless otherwise stated.

### Length generalization after training only at length 40

| Length | 39 | 40 | 41 | 80 | 81 | 160 |
|---|---:|---:|---:|---:|---:|---:|
| NG-StateMin-U1 accuracy | 0.20% | 99.95% | 0.17% | 98.58% | 2.51% | 91.02% |

The near-perfect class inversion on odd lengths is the central negative result. The learned memory is frequently a period-two phase code rather than a time-invariant representation.

### Adding problem, length 40

| Model | Parameters | Mean absolute error |
|---|---:|---:|
| NG-StateMin-U1 | 97 | 0.3189 |
| U1-ReLU | 97 | 0.3195 |
| U1-Tanh | 97 | 0.3137 |
| Elman-ReLU | 697 | 0.1391, high variance |

The proposed cell stores a trace more readily than it accumulates multiple independent events.

### Sequential 8x8 digits, 64 steps

| Model | Parameters | Accuracy |
|---|---:|---:|
| NG-StateMin-U1 | 394 | 25.33% |
| U1-ReLU | 394 | 21.41% |
| U1-Tanh | 394 | 35.78% |
| Elman-Tanh | 1,450 | 84.59% |

This prevents a general claim that the cell replaces standard recurrent neurons.

## Interpretation

The strongest defensible claim is:

> NG-StateMin-U1 is a minimal, parameter-free recurrent transition with an exact period-two memory regime and temporal derivatives restricted to minus one or zero. The same mechanism creates a severe parity-dependent failure mode.

It is presently best viewed as a specialized oscillatory memory primitive or as a starting point for a corrected U2 design—not as a general replacement for RNN, GRU, or LSTM cells.

## Limitations

- Only small CPU experiments were run.
- Most results use three random seeds.
- The sequential-digits experiment is not yet included in the public benchmark script.
- The GRU comparison was not completed in the original run and is not reported as a finished result.
- Novelty has not been established by a systematic literature review.
- Hyperparameter tuning was limited.

## Next experiments

1. Add variable-length training and explicit odd/even stress tests.
2. Compare equal-width, equal-parameter, and equal-FLOP settings separately.
3. Add GRU, LSTM, IRNN, diagonal linear recurrence, MinimalRNN, and UGRNN baselines.
4. Test copy memory, associative recall, permuted sequential MNIST, and long-range arena tasks.
5. Develop a U2 output or phase-compensation mechanism and test whether it removes parity inversion without losing the unit-magnitude memory branch.
