# Principal Theorems

The seven frozen public results, each with its exact Lean declaration, a faithful
English statement, assumptions, direct dependencies, proof technology, edge cases, a
non-vacuity witness, its `#print axioms` output, and a fidelity assessment.

Axiom output is identical for all seven:

```
depends on axioms: [propext, Classical.choice, Quot.sound]
```

(verified by `#print axioms` in `RequestProject/Main.lean`; no `sorryAx`).

---

## 1. `SetPairs.weighted_bollobas`

**File:** `RequestProject/SetPairs/WeightedBollobas.lean`

```lean
theorem weighted_bollobas
    {α ι : Type*} [Fintype α] [DecidableEq α] [Fintype ι] [DecidableEq ι]
    (A B : ι → Finset α)
    (hdiag : ∀ i, Disjoint (A i) (B i))
    (hcross : ∀ ⦃i j⦄, i ≠ j → (A i ∩ B j).Nonempty) :
    ∑ i, ((Nat.choose ((A i).card + (B i).card) (A i).card : ℚ)⁻¹) ≤ 1
```

**English.** For finite families of finite sets `Aᵢ, Bᵢ ⊆ α` that are diagonally
disjoint (`Aᵢ ∩ Bᵢ = ∅`) and cross-intersecting (`Aᵢ ∩ Bⱼ ≠ ∅` for `i ≠ j`),
`∑ᵢ 1 / C(|Aᵢ|+|Bᵢ|, |Aᵢ|) ≤ 1`.

* **Typeclasses.** `α`, `ι` finite with decidable equality.
* **Hypotheses.** `hdiag` (diagonal disjointness), `hcross` (cross-intersection in
  both directions, since `i ≠ j` is symmetric).
* **Direct dependencies.** `card_separationEvent_mul_choose`,
  `separationEvents_pairwiseDisjoint` (← `separationEvents_disjoint`),
  `card_orderEnumerations`.
* **Proof technology.** Permutation counting (separation events over order
  enumerations).
* **Edge cases.** Empty `Aᵢ` or `Bᵢ` are allowed: `C(a+b,a) ≥ 1` so each reciprocal
  is well defined and the count identity `|Eᵢ|·C(|Aᵢ|+|Bᵢ|,|Aᵢ|) = n!` still holds.
  `ι = ∅` gives the empty sum `0 ≤ 1`.
* **Non-vacuity witness.** The uniform complement family
  (`uniform_bollobas_sharp`) with `a = b = 1` on `Fin 2` satisfies both hypotheses
  and has `C(2,1) = 2` members, sum `= 2·(1/2) = 1`. (See `Examples.lean`, the
  `2 * (C 2 1)⁻¹ = 1` check.)
* **Fidelity.** Exactly equivalent to the intended statement. The rational
  denominators are nonzero (`Nat.choose_pos`). No hidden assumption that
  `Aᵢ ∪ Bᵢ = univ`; the ground type may be arbitrarily larger.

---

## 2. `SetPairs.uniform_bollobas`

**File:** `RequestProject/SetPairs/Uniform.lean`

```lean
theorem uniform_bollobas
    {α ι : Type*} [Fintype α] [DecidableEq α] [Fintype ι] [DecidableEq ι] {a b : ℕ}
    (A B : ι → Finset α)
    (hcardA : ∀ i, (A i).card = a)
    (hcardB : ∀ i, (B i).card = b)
    (hdiag : ∀ i, Disjoint (A i) (B i))
    (hcross : ∀ ⦃i j⦄, i ≠ j → (A i ∩ B j).Nonempty) :
    Fintype.card ι ≤ Nat.choose (a + b) a
```

**English.** If in addition every `|Aᵢ| = a` and every `|Bᵢ| = b`, then the number of
indices is at most `C(a+b, a)`.

* **Direct dependencies.** `weighted_bollobas`.
* **Proof technology.** Corollary of the weighted inequality: substitute the constant
  cardinalities, factor the constant reciprocal out of the sum, divide.
* **Edge cases.** `a = 0` and/or `b = 0`: `C(a+b,a) ≥ 1`; the bound still holds.
  `ι = ∅`: `0 ≤ C(a+b,a)`.
* **Non-vacuity witness.** `uniform_bollobas_sharp` gives, for every `a, b`, a family
  attaining `Fintype.card ι = C(a+b, a)` — the bound is tight, hence not vacuous.
* **Fidelity.** Exactly equivalent. Uses `Fintype.card ι` (the genuine finite index
  count), not a `Finset` cardinality.

---

## 3. `SetPairs.uniform_bollobas_sharp`

**File:** `RequestProject/SetPairs/Uniform.lean`

```lean
theorem uniform_bollobas_sharp (a b : ℕ) :
    (∀ S, Disjoint (Sharp.famA a b S) (Sharp.famB a b S)) ∧
    (∀ ⦃S T⦄, S ≠ T → (Sharp.famA a b S ∩ Sharp.famB a b T).Nonempty) ∧
    (∀ S, (Sharp.famA a b S).card = a) ∧
    (∀ S, (Sharp.famB a b S).card = b) ∧
    Fintype.card (Sharp.Index a b) = Nat.choose (a + b) a
```

where `Sharp.Index a b = {S : Finset (Fin (a+b)) // S.card = a}`,
`Sharp.famA a b S = S.1`, `Sharp.famB a b S = S.1ᶜ`.

**English.** On the ground type `Fin (a+b)`, indexing by the `a`-subsets `S` with
`A_S = S`, `B_S = Sᶜ`, the family is diagonally disjoint, cross-intersecting, has all
`|A_S| = a`, all `|B_S| = b`, and exactly `C(a+b, a)` members.

* **Direct dependencies.** None beyond Mathlib (`disjoint_compl_right`,
  `Finset.eq_of_subset_of_card_le`, `Finset.card_add_card_compl`,
  `Fintype.card` of subtype of subsets).
* **Proof technology.** Direct construction.
* **Edge cases.** `a = 0`: the unique index is `∅`, `A = ∅`, `B = univ`, count
  `C(b,0) = 1`. `b = 0`: symmetric.
* **Non-vacuity witness.** It *is* the witness for Theorems 1–2.
* **Fidelity.** Matches the requested "canonical complement family"; it establishes
  sharpness of the uniform bound, **not** a full equality classification (which is
  not claimed anywhere).

---

## 4. `LinearIndependent.of_upperTriangular_maps`

**File:** `RequestProject/LinearAlgebra/TriangularIndependence.lean`

```lean
theorem LinearIndependent.of_upperTriangular_maps
    {K M N : Type*} {m : ℕ}
    [Field K] [AddCommGroup M] [Module K M] [AddCommGroup N] [Module K N]
    (u : Fin m → M) (T : Fin m → M →ₗ[K] N)
    (hdiag : ∀ j, T j (u j) ≠ 0)
    (hzero : ∀ ⦃i j⦄, i < j → T j (u i) = 0) :
    LinearIndependent K u
```

**English.** If a family `u` admits linear "test maps" `T` with `T j (u j) ≠ 0` and
`T j (u i) = 0` whenever `i < j` (upper-triangular annihilation), then `u` is
linearly independent.

* **Typeclasses.** `K` a field; `M, N` `K`-modules. (`Field` is genuinely used: the
  final step divides out a nonzero scalar via `smul_eq_zero`.)
* **Proof technology.** Maximal-nonzero-coefficient argument. From a vanishing
  combination `∑ gᵢ • uᵢ = 0`, let `j = max {i : gᵢ ≠ 0}` and apply `T j`; every
  `i ≠ j` term dies (for `i < j` by `hzero`, for `i > j` because `gᵢ = 0` by
  maximality), leaving `gⱼ • T j (u j) = 0`, contradicting `hdiag`.
* **Orientation check.** `hzero` kills `T j (u i)` for `i < j`; the selected index is
  the **maximal** nonzero coefficient. Orientation and extremum are consistent (see
  `docs/proofs/INDEPENDENT_PROOF_AUDIT.md §3.2`). The dual
  `LinearIndependent.of_lowerTriangular_maps` uses `j < i` and the **minimal** index.
* **Edge cases.** `m = 0`: `LinearIndependent` of the empty family is immediate.
* **Non-vacuity witness.** Any basis with `T j = ` "`j`-th coordinate functional"
  satisfies the hypotheses; concretely used inside `lovasz_frankl_subspaces`.
* **Fidelity.** Exactly the intended generic principle; independent of any set-pairs
  or exterior-algebra notation.

---

## 5. `TwoFamilies.lovasz_frankl_subspaces`

**File:** `RequestProject/LinearAlgebra/TwoFamiliesSubspaces.lean`

```lean
theorem lovasz_frankl_subspaces
    {K V : Type*} [Field K] [AddCommGroup V] [Module K V] [FiniteDimensional K V]
    (a b m : ℕ)
    (hdimV : Module.finrank K V = a + b)
    (U W : Fin m → Submodule K V)
    (hdimU : ∀ i, Module.finrank K (U i) = a)
    (hdimW : ∀ i, Module.finrank K (W i) = b)
    (hdiag : ∀ i, U i ⊓ W i = ⊥)
    (hcross : ∀ ⦃i j⦄, i < j → U i ⊓ W j ≠ ⊥) :
    m ≤ Nat.choose (a + b) a
```

**English.** Over any field `K`, with `dim V = a+b`, subspaces `Uᵢ` (dim `a`), `Wᵢ`
(dim `b`) satisfying `Uᵢ ⊓ Wᵢ = ⊥` and `Uᵢ ⊓ Wⱼ ≠ ⊥` for `i < j`, then
`m ≤ C(a+b, a)`.

* **Direct dependencies.** `LinearIndependent.of_upperTriangular_maps`,
  `append_wedge_ne_zero`, `append_wedge_eq_zero` (← `ExteriorAlgebra.ιMulti_*`,
  `ExteriorAlgebra.ιMulti_mul_ιMulti`, `linearIndependent_append_of_disjoint`,
  `not_linearIndependent_append_of_inf_ne_bot`), `exteriorPower.finrank_eq`,
  `Module.finBasisOfFinrankEq`.
* **Proof technology.** Exterior powers + triangular independence.
* **Skew orientation.** `hcross` uses `i < j` and feeds the **upper**-triangular
  theorem: `T j (u i) = 0` for `i < j`. Consistent (see audit §3.3).
* **Edge cases.** `a = 0`: `Uᵢ = ⊥` forced (dim 0), `uᵢ = ιMulti K 0 = 1 ≠ 0`.
  `b = 0`: `Wⱼ = ⊥`, but `hdiag`/`hcross` become constraints on `⊥ ⊓ ⊥` etc.;
  handled uniformly. `m = 0`: `0 ≤ C(a+b,a)`. No explicit case split is needed
  because empty bases and `ιMulti K 0 = 1` are absorbed by the general argument.
* **Non-vacuity witness.** Take `V = K^{a+b}`, coordinate subspaces; the moment-curve
  construction (`frankl_kalai_skew`) produces genuine instances with `m = C(a+b,a)`
  attained via the sharp set family.
* **Fidelity.** Exactly equivalent; uses the actual lattice meet `⊓` and `= ⊥` (not
  `U i ≠ W i`). Works over an arbitrary field, stronger than a `ℚ`-only statement.

---

## 6. `GeneralPosition.momentCurve_linearIndependent`

**File:** `RequestProject/LinearAlgebra/MomentCurve.lean`

```lean
theorem momentCurve_linearIndependent
    {α : Type*} {d : ℕ} [Fintype α] [DecidableEq α]
    (t : α → ℚ) (ht : Function.Injective t)
    (s : Finset α) (hs : s.card ≤ d) :
    LinearIndependent ℚ (fun x : s => momentCurve d t x)
```

where `momentCurve d t x = fun r : Fin d => t x ^ (r : ℕ)`.

**English.** For an injective label `t : α → ℚ`, any set `s` of at most `d` ground
elements yields linearly independent moment-curve vectors
`(1, tₓ, tₓ², …, tₓ^{d-1})`.

* **Direct dependencies.** Polynomial API (`Polynomial.eval_eq_sum_range`,
  `Polynomial.natDegree_prod`, `Finset.prod_eq_zero`, …). No Vandermonde lemma is
  invoked directly; independence is proved by interpolation.
* **Proof technology.** For a vanishing combination, pick index `i` and evaluate the
  interpolation polynomial `p = ∏_{j≠i}(X - t_j)` (degree `|s|-1 < d`) against the
  moment relations `∑ⱼ uⱼ tⱼ^r = 0`; only the `i`-term survives, forcing `uᵢ = 0`.
* **`|s| < d` case.** Handled: the argument never needs `|s| = d`. `p` has degree
  `|s|-1`, always `< d`; only the first `|s|` coordinate relations are used. No square
  matrix / exactly-`d` assumption is smuggled in.
* **Edge cases.** `s = ∅`: empty family is independent. `d = 0` forces `s = ∅`
  (`hs : |s| ≤ 0`).
* **Non-vacuity witness.** `t = ` the canonical `α ≃ Fin (card α)` label cast to `ℚ`
  is injective; used in `frankl_kalai_skew`.
* **Fidelity.** Exactly the intended rectangular general-position statement over `ℚ`.

---

## 7. `SetPairs.frankl_kalai_skew`

**File:** `RequestProject/SkewSetPairs.lean`

```lean
theorem frankl_kalai_skew
    {α : Type*} [Fintype α] [DecidableEq α] {m a b : ℕ}
    (A B : Fin m → Finset α)
    (hcardA : ∀ i, (A i).card = a)
    (hcardB : ∀ i, (B i).card = b)
    (hdiag : ∀ i, Disjoint (A i) (B i))
    (hcross : ∀ ⦃i j⦄, i < j → (A i ∩ B j).Nonempty) :
    m ≤ Nat.choose (a + b) a
```

**English.** For skew cross-intersecting (`i < j`), diagonally disjoint, uniform
(`|Aᵢ| = a`, `|Bᵢ| = b`) set pairs indexed by `Fin m`, `m ≤ C(a+b, a)`.

* **Direct dependencies.** `TwoFamilies.lovasz_frankl_subspaces`,
  `GeneralPosition.spanMomentCurve`, `finrank_spanMomentCurve`,
  `inf_spanMomentCurve_eq_bot`, `inf_spanMomentCurve_ne_bot`,
  `Module.finrank_fin_fun`, `Fintype.equivFin`.
* **Proof technology.** Moment-curve general-position bridge into `ℚ^{a+b}` +
  subspace theorem.
* **Ground set larger than `a+b`.** Explicitly supported: `α` is arbitrary finite,
  labelled injectively into `ℚ` via `Fintype.equivFin`; only `d = a+b` bounds the
  ambient dimension, never `|α|`.
* **Edge cases / `d = 0`.** When `a+b = 0`, the proof splits: `a = 0` makes `Aᵢ = ∅`,
  contradicting `hcross`'s nonempty intersection when `m ≥ 2`; for `m ≤ 1` the bound
  `1 ≤ C(0,0) = 1` holds. This case is handled explicitly (`by_cases hd0 : d = 0`).
* **Non-vacuity witness.** The sharp complement family on `Fin (a+b)` (a subset of an
  arbitrary `α`) with any linear ordering of indices attains `m = C(a+b,a)`.
* **Fidelity.** Exactly equivalent; uses `i < j` skew direction (strictly weaker
  hypothesis than the symmetric `i ≠ j`), hence a stronger theorem than the symmetric
  uniform bound.

---

## Fidelity summary

| # | Theorem | vs. intended |
|---|---------|--------------|
| 1 | `weighted_bollobas` | exactly equivalent |
| 2 | `uniform_bollobas` | exactly equivalent |
| 3 | `uniform_bollobas_sharp` | equivalent (sharpness only, no equality classification) |
| 4 | `of_upperTriangular_maps` | exactly equivalent (generic) |
| 5 | `lovasz_frankl_subspaces` | equivalent; general field (stronger than ℚ-only) |
| 6 | `momentCurve_linearIndependent` | exactly equivalent |
| 7 | `frankl_kalai_skew` | equivalent; skew `i<j` (stronger than symmetric) |

No public statement was changed during this revision.
