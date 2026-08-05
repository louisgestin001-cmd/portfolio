# NG-TriSpecies-1:2:3

## Status

NG-TriSpecies is an experimental heterogeneous feed-forward block rather than a recurrent cell. It is included in NG Cell Lab because it extends the same research program: invent a compact law, implement it exactly, compare it with strong baselines, and document both gains and failure modes.

The provisional name is retained, although the stated population fractions correspond to an A:B:C ratio of approximately **3:2:1**:

- species A: 50%;
- species B: about 33%;
- species C: about 17%.

## Law

Given three conceptual learned projections

\[
p_0=W_0x,\qquad p_1=W_1x,\qquad p_2=W_2x,
\]

the hidden coordinates are split into three groups.

### Species A — compressive conservative branch

\[
m=\min(p_0,p_1),
\qquad
\phi_A=\operatorname{sign}(m)\log(1+|m|).
\]

Only the lower projection passes, and large magnitudes are softly compressed.

### Species B — hard conservative selector

\[
\phi_B=\min(p_0,p_2).
\]

A strongly positive coordinate requires both projections to be compatible; a low value in either projection suppresses it.

### Species C — divisively regulated branch

\[
\phi_C=\frac{p_2}{1+|p_0|}.
\]

The magnitude of one projection regulates another without a sigmoid gate.

The outputs are concatenated and projected:

\[
h=[\phi_A;\phi_B;\phi_C],
\qquad y=W_{\mathrm{down}}h.
\]

## Efficient implementation

The public implementation computes only the projection slices used by each species:

- all of `p0`;
- the A slice of `p1`;
- the B and C slices of `p2`.

This is equivalent to computing three full projections and discarding unused coordinates. With input width 64, hidden width 64, and output width 10, it has **8,970 parameters**, exactly matching a same-width SwiGLU or GEGLU classifier.

## Preliminary results

The exploratory Digits benchmark used five random seeds and approximately 9,000 parameters per model.

| Block | Clean accuracy | 20% training data | Noise 0.4 |
|---|---:|---:|---:|
| GELU | 97.33% | 93.96% | 63.56% |
| ReLU | 97.82% | 94.27% | 65.85% |
| SwiGLU | 97.87% | 94.09% | 64.07% |
| GEGLU | 98.04% | 94.31% | 63.78% |
| **NG-TriSpecies 3:2:1** | **98.49%** | **95.78%** | **69.26%** |

The strongest initial signal is robustness under reduced data and Gaussian corruption, not the small clean-data gain.

## Critical ablation

| Variant | Clean accuracy |
|---|---:|
| Species A only | 98.53% |
| Species B only | 98.44% |
| Species C only | 98.44% |
| TriSpecies 1:1:1 | 98.53% |
| TriSpecies 3:2:1 | 98.49% |

This prevents a stronger claim: the current experiment **does not prove that heterogeneous species or the proposed ratio caused the gain**. Species A alone and the equal mixture were at least as strong on the clean Digits task.

Possible explanations include:

1. the signed-log minimum is itself a strong activation;
2. hard minimum operators provide useful robustness;
3. diversity matters mainly under corruption or on larger tasks;
4. the fixed 3:2:1 ratio is not optimal;
5. learned routing or learned ratios may be needed.

## Gradient properties

For species A, away from the minimum boundary, the active projection receives slope

\[
\frac{1}{1+|m|},
\]

which is bounded and decreases smoothly with magnitude. The non-selected projection generally receives zero gradient.

Species B routes gradient through the smaller projection only.

For species C,

\[
\frac{\partial\phi_C}{\partial p_2}=\frac{1}{1+|p_0|},
\]

and

\[
\frac{\partial\phi_C}{\partial p_0}
=-\frac{p_2\operatorname{sign}(p_0)}{(1+|p_0|)^2}.
\]

The branch is a true divisive interaction but may produce sharp optimization changes around hard branch boundaries.

## Cost warning

The naive PyTorch implementation uses several separate operations (`minimum`, `abs`, `log1p`, division, concatenation). Preliminary CPU measurements found it materially slower than SwiGLU or GEGLU. A fused GPU kernel would be needed before claiming practical efficiency in a large language model.

## Next decisive experiment

Replace the feed-forward block of the same small Transformer with:

1. GELU;
2. SwiGLU;
3. GEGLU;
4. species A only;
5. TriSpecies 1:1:1;
6. TriSpecies 3:2:1;
7. a learned species allocation.

Compare validation loss, sequence-length extrapolation, algorithmic reasoning, robustness, throughput, activation statistics, and at least ten seeds. Until then, NG-TriSpecies should be described as a **promising heterogeneous MLP candidate**, not a validated new general family.
