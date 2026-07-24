# Mathlib extraction plan

Generic results developed here that could be upstreamed to Mathlib, with proposed
locations and dependency notes. Project-specific wrappers (the two-families
theorems themselves) are **not** proposed for upstreaming as-is.

## 1. Triangular linear independence from linear maps

* Declaration: `LinearIndependent.of_upperTriangular_maps` (and the lower dual).
* Proposed path: `Mathlib/LinearAlgebra/LinearIndependent/Basic.lean` (or a new
  `.../TriangularIndependence.lean`).
* Statement: for `u : Fin m → M`, `T : Fin m → M →ₗ[K] N` with `T j (u j) ≠ 0`,
  `T j (u i) = 0` for `i < j`, conclude `LinearIndependent K u`.
* Imports: linear independence, `Fintype.linearIndependent_iff`.
* Genuinely general: yes; index by any `LinearOrder` `Fintype` would be a natural
  generalization.

## 2. Nonvanishing of decomposable exterior products

* Declarations: `ExteriorAlgebra.ιMulti_ne_zero_of_linearIndependent`,
  `exteriorPower.ιMulti_ne_zero_of_linearIndependent`.
* Proposed path: `Mathlib/LinearAlgebra/ExteriorPower/Basic.lean` (companion to the
  existing `ιMulti_family_linearIndependent_field`).
* Dependency direction: complements the existing vanishing direction
  (`AlternatingMap.map_linearDependent`).
* Genuinely general: yes (any field; a torsion-free target more generally).

## 3. Concatenation of decomposable exterior products

* Declaration: `ExteriorAlgebra.ιMulti_mul_ιMulti`.
* Proposed path: `Mathlib/LinearAlgebra/ExteriorAlgebra/Basic.lean`.
* Statement: `ιMulti R a u * ιMulti R b w = ιMulti R (a+b) (Fin.append u w)`.
* Imports: `ExteriorAlgebra.ιMulti_apply`, `List.ofFn`, `Fin.append`.
* Genuinely general: yes (any commutative base ring).

## 4. Finite moment-curve general position

* Declarations: `GeneralPosition.momentCurve`,
  `GeneralPosition.momentCurve_linearIndependent` and the span consequences.
* Proposed path: `Mathlib/LinearAlgebra/Vandermonde.lean` or
  `Mathlib/LinearAlgebra/GeneralPosition.lean` (new).
* Statement: distinct moment-curve vectors (`≤ d` of them) are independent over any
  field with an injective label; disjoint/intersecting span lemmas.
* Note: the current proof is over `ℚ`; a field-generic version is the natural
  upstream form.
* Genuinely general: yes, once generalized from `ℚ` to an arbitrary field.

## 5. Order-enumeration counting

* Declaration: `SetPairs.card_orderEnumerations` (a thin wrapper over
  `Fintype.card_equiv`) and the exact separation-event count
  `SetPairs.card_separationEvent_mul_choose`, together with its closed form
  `SetPairs.card_separationEvent_eq`.
* The count (number of linear orders separating a disjoint pair) is a genuinely
  general counting lemma suitable for `Mathlib/Combinatorics/`. Its proof factors
  through three reusable ingredients also worth upstreaming: `card_separates_full`
  (linear orders of an `(a+b)`-set placing a fixed `a`-subset first, count `a!·b!`),
  `card_separates_toP` (the same count against an arbitrary ordered `(a+b)`-set via
  transport along `orderIsoOfFin`), and `fiber_card_eq` (the ordering-factorization
  fibre equivalence over the position set).

## 6. Set-pairs predicates and API

* `SetPairs.DiagonallyDisjoint`, `CrossIntersecting`, `SkewCrossIntersecting` plus
  the symmetry/restriction/reindexing lemmas.
* These are lightweight and could live in `Mathlib/Combinatorics/SetFamily/`.
* Lower priority: small enough that upstreaming is optional.
