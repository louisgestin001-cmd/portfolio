# Mathlib PR Plan

A concrete, reviewable extraction sequence. **No Mathlib modification or PR is opened**
— this is a plan only, as the task requires. Diff-size estimates count project lines
plus the anticipated generalization overhead.

Ordering is by dependency: earlier PRs are prerequisites for later ones.

---

## PR 1 — Triangular independence from linear maps

* **Declarations:** `LinearIndependent.of_upperTriangular_maps`,
  `LinearIndependent.of_lowerTriangular_maps`.
* **Proposed path:** `Mathlib/LinearAlgebra/LinearIndependent/Lemmas.lean` (or a new
  `Mathlib/LinearAlgebra/LinearIndependent/Triangular.lean`).
* **Minimal imports:** `Mathlib.LinearAlgebra.LinearIndependent.Defs`,
  `Mathlib.Data.Fintype.Card`, `Mathlib.Order.Fin.Basic`.
* **Dependency order:** none (self-contained).
* **Estimated diff:** ~90 lines (both directions), ~120 with docstrings/generalization.
* **Should stay outside Mathlib:** nothing; fully generic.
* **Generalization for upstream:** index by any `[LinearOrder ι] [Fintype ι]` rather
  than `Fin m`; keep `Field K` (the divide-out step needs it) or generalize to a
  domain where `smul_eq_zero` holds.
* **Expected reviewer objections:** "Is this subsumed by existing
  `LinearIndependent.of_*`?" — answer: no Mathlib lemma derives independence from a
  triangular family of *test maps*; nearest is `LinearIndependent.of_comp`, which is
  different. Possible request to unify with a matrix-triangularity statement.
* **PR description (draft):** "Add `LinearIndependent.of_upperTriangular_maps`: a
  family is independent if it admits test maps that are diagonal-nonzero and
  strictly-upper-triangular-annihilating. Proof by maximal-nonzero-coefficient. Plus
  the lower dual."
* **AI disclosure:** PR body to state the proof was drafted with AI assistance and
  kernel-checked.

## PR 2 — Decomposable exterior vectors: nonvanishing and concatenation

* **Declarations:** `ExteriorAlgebra.ιMulti_ne_zero_of_linearIndependent`,
  `exteriorPower.ιMulti_ne_zero_of_linearIndependent`,
  `ExteriorAlgebra.ιMulti_mul_ιMulti` (and the thin re-export
  `ιMulti_eq_zero_of_linearDependent` if wanted, else cite
  `AlternatingMap.map_linearDependent` directly).
* **Proposed path:** `Mathlib/LinearAlgebra/ExteriorPower/Basic.lean` (nonvanishing,
  companion to `ιMulti_family_linearIndependent_field`) and
  `Mathlib/LinearAlgebra/ExteriorAlgebra/Basic.lean` (concatenation).
* **Minimal imports:** `Mathlib.LinearAlgebra.ExteriorPower.Basic`,
  `Mathlib.LinearAlgebra.ExteriorAlgebra.Basic`.
* **Dependency order:** none on PR 1; independent.
* **Estimated diff:** ~110 lines (concatenation is the bulk, via the
  `List.ofFn`/`Fin.append` equality).
* **Should stay outside Mathlib:** nothing.
* **Generalization:** nonvanishing over any field (target torsion-free);
  concatenation over any `CommRing`.
* **Expected reviewer objections:** the concatenation lemma's `List.ofFn` induction is
  verbose; a reviewer may ask for a slicker proof via `Fin.append` API or existing
  graded-multiplication lemmas. Nonvanishing might be requested as an `iff` with the
  existing vanishing direction.
* **PR description:** "Complete the vanishing↔nonvanishing characterization of
  decomposable `ιMulti` (currently only the dependent⇒0 direction exists), and add the
  concatenation identity `ιMulti a u * ιMulti b w = ιMulti (a+b) (Fin.append u w)`."
* **AI disclosure:** as PR 1.

## PR 3 — Moment-curve general position

* **Declarations:** `GeneralPosition.momentCurve`, `momentCurve_ne_zero`,
  `momentCurve_linearIndependent`, `spanMomentCurve`, `finrank_spanMomentCurve`,
  `inf_spanMomentCurve_eq_bot`, `inf_spanMomentCurve_ne_bot`.
* **Proposed path:** new `Mathlib/LinearAlgebra/GeneralPosition/MomentCurve.lean`.
* **Minimal imports:** `Mathlib.LinearAlgebra.Vandermonde`,
  `Mathlib.LinearAlgebra.Dimension.Finrank`, `Mathlib.Algebra.Polynomial.Eval`.
* **Dependency order:** independent of PR 1–2.
* **Estimated diff:** ~200 lines.
* **Should stay outside Mathlib:** possibly the span-intersection corollaries if
  reviewers deem them too application-specific; the core independence theorem is
  clearly generic.
* **Generalization:** replace `ℚ` by any infinite field (or any field with `≥ d`
  elements); the interpolation proof works verbatim over a field.
* **Expected reviewer objections:** "why not derive from `Matrix.det_vandermonde`?" —
  answer: the rectangular `|s| < d` case needs the interpolation argument anyway;
  provide both if desired. Naming (`momentCurve` vs. `Polynomial`-based) may be
  debated.
* **PR description:** "Add moment-curve (Vandermonde) general position: ≤ `d` distinct
  moment vectors over a field are independent, with span-dimension and
  span-intersection consequences."
* **AI disclosure:** as PR 1.

## PR 4 — Finite-ordering / separation-event combinatorics

* **Declarations:** `SetPairs.card_orderEnumerations` (thin; maybe omit),
  `card_separates_full`, `card_separates_toP`, `fiber_card_eq`,
  `card_separationEvent_eq`, `card_separationEvent_mul_choose`.
* **Proposed path:** new `Mathlib/Combinatorics/Enumeration/SeparationCount.lean`.
* **Minimal imports:** `Mathlib.Combinatorics.Enumerative.*`,
  `Mathlib.Data.Fintype.Perm`, `Mathlib.Data.Nat.Choose.Factorization`,
  `Mathlib.Order.Fin.Basic`.
* **Dependency order:** independent.
* **Estimated diff:** ~450 lines (the largest; the ordering-factorization equivalence
  is intricate).
* **Should stay outside Mathlib:** the thin `card_orderEnumerations` wrapper.
* **Generalization:** state over an arbitrary finite `α` and disjoint `A B : Finset α`
  (already the form used). Could be phrased for `Finset.orderIsoOfFin`-style orders.
* **Expected reviewer objections:** size; request to split into the
  full-support lemma + fibre equivalence + summation as separate PRs. Naming of
  `Separates`/`separationEvent`.
* **PR description:** "Count linear orders of a finite set that place one part of a
  disjoint pair entirely before the other: closed form `C(n,a+b)·a!·b!·(n−a−b)!` and
  the clean identity `count · C(a+b,a) = n!`."
* **AI disclosure:** as PR 1.

## PR 5 — Two-families application

* **Declarations:** `SetPairs.DiagonallyDisjoint`, `CrossIntersecting`,
  `SkewCrossIntersecting` (+ API), `weighted_bollobas`, `uniform_bollobas`,
  `uniform_bollobas_sharp`, `lovasz_frankl_subspaces`, `frankl_kalai_skew`.
* **Proposed path:** `Mathlib/Combinatorics/SetFamily/TwoFamilies.lean` and
  `Mathlib/LinearAlgebra/TwoFamilies.lean`.
* **Dependency order:** requires PRs 1–4 landed.
* **Estimated diff:** ~350 lines.
* **Should stay outside Mathlib:** nothing mathematically, but this is the
  application layer and should only be proposed once the infrastructure PRs have
  settled APIs.
* **Expected reviewer objections:** whether the predicates deserve top-level names;
  whether the subspace theorem should be stated more generally (skew families over a
  poset). Sharpness could be asked to be strengthened toward equality classification.
* **PR description:** "Bollobás set-pairs inequality (weighted + uniform + sharpness),
  Lovász–Frankl subspace two-families theorem, and Frankl–Kalai skew set theorem."
* **AI disclosure:** as PR 1.

---

## Declarations recommended to stay OUT of Mathlib

* `card_orderEnumerations` (one-liner over `Fintype.card_equiv`).
* `ιMulti_eq_zero_of_linearDependent` if it remains a pure re-export of
  `AlternatingMap.map_linearDependent`.
* `RequestProject/Examples.lean`, `Main.lean` (project glue, not library content).

## Summary table

| PR | Theme | Est. lines | Depends on | Genuinely generic? |
|----|-------|-----------|------------|--------------------|
| 1 | Triangular independence | ~120 | — | yes |
| 2 | Exterior decomposables | ~110 | — | yes |
| 3 | Moment-curve GP | ~200 | — | yes (over any field) |
| 4 | Separation-event counting | ~450 | — | yes |
| 5 | Two-families application | ~350 | 1–4 | yes (application) |
