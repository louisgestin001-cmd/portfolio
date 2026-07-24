# Adversarial Theorem Testing

We attempt to break each principal theorem by removing hypotheses, and determine
whether the weakened claim is **false**, **still true**, or **unknown**. All
counterexamples use exact arithmetic (`fractions.Fraction`, exact rank over ℚ) and are
reproduced by `scripts/adversarial_checks.py` (`OVERALL: PASS`). Numeric fragments are
additionally checked in Lean in `RequestProject/Examples.lean`.

The goal is to demonstrate the hypotheses are meaningful and sharp — **not** to weaken
the real theorems.

| # | Theorem | Hypothesis dropped | Result | Witness |
|---|---------|--------------------|--------|---------|
| 1 | weighted_bollobas | diagonal disjointness `hdiag` | **FALSE** | 3×(A=B={0}), sum 3/2 |
| 2 | weighted_bollobas | full cross → skew only (i<j) | **FALSE** | ground {0,1,2}, sum 4/3 |
| 3 | frankl_kalai_skew | direction `i<j` reversed to `i>j` | **still TRUE** | relabel k↦m−1−k |
| 4 | frankl_kalai_skew | uniformity `|Aᵢ|=a,|Bᵢ|=b` | **FALSE** | same as #2 (non-uniform, sum>bound) |
| 5 | lovasz_frankl_subspaces | `Uᵢ⊓Wᵢ=⊥` → `≠⊤` | **FALSE** | see below |
| 6 | momentCurve_linearIndependent | injectivity of `t` | **FALSE** | labels [2,2] |
| 7 | momentCurve_linearIndependent | `|s|≤d` | **FALSE** | d=1, labels [0,1] |
| 8 | inf_spanMomentCurve_eq_bot | `|S|+|T|≤d` | **FALSE** | d=1, S={0},T={1} |

---

## 1. Weighted Bollobás without diagonal disjointness — FALSE

Ground `{0}`, three identical pairs `Aᵢ = Bᵢ = {0}`. Cross-intersecting holds
(`Aᵢ ∩ Bⱼ = {0} ≠ ∅` for `i ≠ j`), diagonal disjointness fails. Sum
`= 3 · 1/C(2,1) = 3/2 > 1`. Hence `hdiag` is load-bearing.

Lean numeric witness (`Examples.lean`): `3 * (C 2 1)⁻¹ = 3/2` and `¬ (3/2 ≤ 1)`.

## 2. Weighted Bollobás with only skew cross-intersection — FALSE

Ground `{0,1,2}`, pairs `({0},{1}), ({1},{0}), ({2},{0,1})`. Diagonally disjoint;
skew cross-intersecting (`Aᵢ∩Bⱼ ≠ ∅` for `i<j`); but **full** cross-intersection
fails (`A₂∩B₀ = {2}∩{1} = ∅`). Sum `= 1/2 + 1/2 + 1/3 = 4/3 > 1`. So the weighted
inequality genuinely requires cross-intersection in **both** index directions
(`i ≠ j`), which the Lean statement enforces.

## 3. Frankl–Kalai skew with the direction reversed — STILL TRUE

Replacing `i < j` by `i > j` in `hcross` is the reindexing `k ↦ m−1−k`, an
order-reversing bijection of `Fin m`. Both hypothesis and conclusion are invariant, so
the reversed statement is *equivalent*, hence still true. This is not a weakness: it
shows the choice of orientation is a labelling convention, and the proof's use of the
**upper**-triangular principle is matched to the chosen `i<j` convention.

## 4. Frankl–Kalai skew without uniformity — FALSE

The witness of #2 is diagonally disjoint and skew cross-intersecting with `m = 3`, but
sizes are non-uniform (`|A₂| = 1`, `|B₂| = 2`). If one dropped the uniform-size
hypotheses and asked for a single bound `m ≤ C(a+b,a)` the claim becomes ill-posed;
the weighted-style sum already exceeds 1, so no uniform binomial bound governs the
non-uniform skew case. Uniformity (`hcardA`, `hcardB`) is essential — it is exactly
what makes the moment-curve dimensions `a` and `b` constant.

## 5. Subspace theorem with `Uᵢ ⊓ Wᵢ ≠ ⊤` instead of `= ⊥` — FALSE

`Uᵢ ⊓ Wᵢ ≠ ⊤` is a far weaker (and, for `dim V = a+b ≥ 1`, essentially always-true)
condition than `Uᵢ ⊓ Wᵢ = ⊥`. Concretely take `V = ℚ²`, `a = b = 1`, and let every
`Uᵢ = Wᵢ = span{e₁}`. Then `Uᵢ ⊓ Wᵢ = span{e₁} ≠ ⊤` (it is a proper subspace), so the
`≠⊤` variant is satisfied, yet the diagonal decomposable `uᵢ ∧ wᵢ = e₁ ∧ e₁ = 0`
vanishes and the argument collapses — one can take `m` arbitrarily large with all
`Uᵢ = Wᵢ`, violating `m ≤ C(2,1) = 2`. The real hypothesis `Uᵢ ⊓ Wᵢ = ⊥`
(diagonal *transversality*) is indispensable; `≠⊤` is not a substitute.

## 6. Moment curve with non-injective labels — FALSE

Labels `[2, 2]`, `d = 3`: the two moment vectors `(1,2,4)` coincide, rank `1 < 2`,
dependent. `ht : Function.Injective t` is load-bearing (it is exactly what makes
`p(tᵢ) ≠ 0` in the interpolation step).

## 7. Moment curve with too many vectors — FALSE

`d = 1`, labels `[0, 1]`: both vectors equal `(1)` in `ℚ¹`, rank `1 < 2`, dependent.
The bound `|s| ≤ d` is load-bearing; the proof does **not** secretly require `|s| = d`
(see `docs/proofs/INDEPENDENT_PROOF_AUDIT.md §3.4`) but it does require `|s| ≤ d`.

## 8. Span trivial-intersection lemma when `|S|+|T| > d` — FALSE

`d = 1`, `S = {0}`, `T = {1}` disjoint, `|S|+|T| = 2 > 1`. Each span is all of `ℚ¹`,
so `span(S) ⊓ span(T) = ℚ¹ ≠ ⊥` (computed intersection dimension `1`). The cardinality
bound `|S|+|T| ≤ d` in `inf_spanMomentCurve_eq_bot` is load-bearing.

---

## Reproduction

```bash
python3 scripts/adversarial_checks.py     # exact-arithmetic, prints OVERALL: PASS
lake build RequestProject.Examples        # Lean numeric adversarial checks
```

The `decide`/`norm_num` adversarial numeric facts (#1) live in `Examples.lean`. Cases
#5 is an algebraic argument (no finite decision procedure); it is recorded here and in
the audit rather than as a decidable Lean example.
