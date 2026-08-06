# Local finite-difference identification of guarded affine programs

## Observation model

Let the hidden integer state be \(x_w\in\mathbb Z^d\) after word \(w\), and suppose the black-box response is

\[
F(w)=H x_w+c,
\]

where \(H\in\mathbb R^{m\times d}\) has full column rank.

Assume the learner has identified local coordinate actions \(t_i\) satisfying

\[
t_i(0)=e_i.
\]

Define

\[
V=\begin{bmatrix}
F(t_1)-F(\varepsilon)&\cdots&F(t_d)-F(\varepsilon)
\end{bmatrix}=H.
\]

More generally, the columns may form any invertible integer coordinate basis; the reconstructed program is then expressed in that basis.

## Singular affine maps are identifiable

Suppose action \(a\) is affine on a region containing the anchor and its coordinate neighbours:

\[
a(x)=M_a x+b_a.
\]

Then

\[
F(a)-F(\varepsilon)=H b_a,
\]

and

\[
F(t_i a)-F(a)=H M_a e_i.
\]

Therefore

\[
\boxed{b_a=V^+\big(F(a)-F(\varepsilon)\big)}
\]

and

\[
\boxed{M_a e_i=V^+\big(F(t_i a)-F(a)\big)}.
\]

No inverse of \(M_a\) or of action \(a\) is required. Constant resets, projections and other singular maps are covered by the same identity.

## Guarded actions

For a piecewise-affine transition

\[
a(x)=M_jx+b_j\quad\text{when }x\in R_j,
\]

the same identity applies separately inside every region. NG-GuardedAffine-CEGIS:

1. fits an affine hypothesis from a small set of states;
2. searches the bounded verification grid for the first state that refutes it;
3. adds that counterexample;
4. introduces an axis-aligned threshold only when no single affine map explains the accumulated states;
5. repeats until exhaustive transition agreement is obtained.

For the protocol benchmark, eight counterexamples recover all ten actions. The deepest rule is `timeout`, with depth two and three affine regions.

## Limits

The identification guarantee requires:

- a full-rank observation of the latent coordinates;
- locally valid translation probes;
- guards representable by the threshold grammar;
- enough separation to round noisy decoded coordinates to integers.

A nonlinear observation, hidden coordinates in the kernel of \(H\), diagonal guards, or state-dependent basis actions can break the current implementation.
