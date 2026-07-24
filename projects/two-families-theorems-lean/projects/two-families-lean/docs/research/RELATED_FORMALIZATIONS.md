# Related formalizations

This note documents a search for prior formalizations of the results in this
project. The search is necessarily incomplete; we use cautious wording.

## Search performed

* **Mathlib** (`v4.28.0`): searched the source tree for `bollobas`, `two-families`,
  `set-pairs`, `Frankl`, `Lovász`, skew-intersecting families, and the exterior /
  moment-curve infrastructure. Mathlib provides exterior powers
  (`Mathlib.LinearAlgebra.ExteriorPower.*`), the graded exterior algebra, the
  Vandermonde determinant, and the LYM inequality
  (`Mathlib.Combinatorics.SetFamily.LYM`), but **no** Bollobás set-pairs
  inequality, uniform/skew two-families theorem, or Lovász subspace theorem was
  found.
* **LeanSearch / Loogle**: queried for the statements above; no matching Lean
  declarations were surfaced.
* **Other libraries** (Isabelle AFP, Rocq/Coq, HOL Light/HOL4, Mizar): we are not
  aware of a formalization of the weighted Bollobás inequality, the skew
  Frankl–Kalai theorem, or the exterior-algebra proof of the Lovász subspace
  theorem in these systems. The Isabelle AFP contains substantial extremal
  set-theory developments, but we did not locate these specific theorems.

## Building blocks that DO exist upstream

* Exterior powers and their dimension `exteriorPower.finrank_eq` (Mathlib).
* `AlternatingMap.map_linearDependent` (vanishing on dependent inputs) (Mathlib).
* `Matrix.det_vandermonde` (Mathlib).
* LYM inequality via shadows (Mathlib) — a different chain-counting technique.

## Statement of novelty (cautious)

> To the best of our documented search, we found no prior Lean formalization of the
> complete chain of weighted, skew-set, and subspace two-families theorems, nor of
> the permutation-counting and exterior-power proofs presented here.

We make no stronger claim. If a prior formalization exists, a proper comparison
would cover: generality (arbitrary finite ground types vs. `Fin n`), proof method
(permutation counting vs. exterior algebra vs. tensor methods), equality/sharpness
results, reusable infrastructure, and the proof assistant used.
