# Formalization notes

## Permutation-counting route (Theorems 1–2)

* **Order enumerations.** A total order on a finite type `α` is modelled as an
  `Equiv` `α ≃ Fin (card α)` (`SetPairs.OrderEnumeration`). The number of these is
  `(card α)!` (`SetPairs.card_orderEnumerations`), a one-line consequence of
  `Fintype.card_equiv`.
* **Separation events.** `SetPairs.Separates e A B` says every element of `A`
  precedes every element of `B` under `e`. The event `separationEvent A B` is the
  corresponding `Finset` of order enumerations.
* **Exact count.** `card_separationEvent_mul_choose` states
  `|separationEvent A B| · C(|A|+|B|, |A|) = (card α)!` for disjoint `A`, `B`.
  This is the exact (non-probabilistic) heart of the argument. It follows from the
  closed-form count `card_separationEvent_eq`,
  `|separationEvent A B| = C(n, a+b)·a!·b!·(n-(a+b))!`, proved by an
  ordering-factorization equivalence: a separating enumeration is the data of the
  `(a+b)`-element position set `P = e(A∪B)`, the relative order of `A∪B` inside `P`
  (with `A` before `B`), and the relative order of the complement inside `Pᶜ`.
  The supporting lemmas are `card_separates_full` (full-support case, two explicit
  injections + order statistics), `card_separates_toP` (transport along
  `P ≃o Fin(a+b)`), and `fiber_card_eq` (fixed-`P` fibre), summed over the `C(n,a+b)`
  position sets via `Finset.card_eq_sum_card_fiberwise`. No natural-number division is
  used; the final identity is `Nat.choose_mul_factorial_mul_factorial`.
* **Disjointness.** `separationEvents_disjoint`: if `x ∈ A_i ∩ B_j` and
  `y ∈ A_j ∩ B_i`, then separating `(A_i,B_i)` forces `e x < e y` while separating
  `(A_j,B_j)` forces `e y < e x` — impossible. Hence the events are pairwise
  disjoint (`separationEvents_pairwiseDisjoint`).
* **Assembly.** Each reciprocal equals `|E_i| / (card α)!`; summing the pairwise
  disjoint cardinalities gives `∑ |E_i| ≤ (card α)!`, hence the bound (`weighted_bollobas`).
  The uniform corollary factors out the constant term and divides
  (`uniform_bollobas`); sharpness is the complement family (`uniform_bollobas_sharp`).

## Exterior-power route (Theorems 3–4–5)

* **Triangular independence.** `LinearIndependent.of_upperTriangular_maps`: given
  test maps `T j` with `T j (u j) ≠ 0` and `T j (u i) = 0` for `i < j`, the `u i`
  are independent. Proof: apply `T j` at the largest index `j` with nonzero
  coefficient in a vanishing combination. A dual lower-triangular version is
  included.
* **Decomposable exterior vectors.** `ExteriorAlgebra.ιMulti K r v` is the wedge
  `v 0 ∧ ⋯ ∧ v (r-1)`. It vanishes iff `v` is linearly dependent
  (`ιMulti_eq_zero_of_linearDependent` from `AlternatingMap.map_linearDependent`,
  and `ιMulti_ne_zero_of_linearIndependent`). Concatenation
  (`ιMulti_mul_ιMulti`) turns a product of decomposables into the decomposable of
  the `Fin.append` family.
* **Subspace theorem.** For each `i` pick bases of `U_i`, `W_i`, forming
  `u_i ∈ ⋀^a V` and a test map `T_j = (· * w_j) ∘ subtype`. Then
  `T_j (u_i) = ExteriorAlgebra.ιMulti K (a+b) (append (bU_i) (bW_j))`, nonzero on
  the diagonal (`U_i ⊓ W_i = ⊥`) and zero for `i < j` (`U_i ⊓ W_j ≠ ⊥`). Triangular
  independence bounds `m ≤ dim ⋀^a V = C(a+b, a)` via `exteriorPower.finrank_eq`.
  No case split on `a`, `b`, `m = 0` is needed: empty bases and `ιMulti K 0 = 1`
  are handled uniformly, and contradictory cross-intersection hypotheses
  (`U_i = ⊥`) make the vanishing lemma vacuously applicable.
* **Moment curve.** `momentCurve d t x = (t x^r)_{r<d}`. Linear independence of at
  most `d` distinct such vectors (`momentCurve_linearIndependent`) is proved by
  polynomial interpolation: for the target index `i`, the polynomial
  `∏_{j≠i}(X - t_j)` vanishes at all other `t_j` and not at `t_i`, forcing the
  coefficient to vanish. Span/intersection consequences give
  `finrank_spanMomentCurve`, `inf_spanMomentCurve_eq_bot`,
  `inf_spanMomentCurve_ne_bot`.
* **Bridge.** `frankl_kalai_skew` labels the finite ground type injectively into
  `ℚ` (via `Fintype.equivFin`), realises each set as a moment-curve span in
  `ℚ^{a+b}`, and applies the subspace theorem.

## Conventions

* Rational arithmetic (`ℚ`) is used throughout the counting argument; no floating
  point.
* Cross-intersection is stated with implicit binders `⦃i j⦄` and, for the skew
  results, with the strict order `i < j` on `Fin m`.
