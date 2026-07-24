# Theorem map

Informal statements paired with their Lean formalizations.  All Lean names are
fully qualified; file paths are relative to the project root.

## 1. Bollobás's weighted set-pairs inequality

**Informal.** Let `α`, `ι` be finite. For `A_i, B_i ⊆ α` with `A_i ∩ B_i = ∅` for
all `i` and `A_i ∩ B_j ≠ ∅` for all `i ≠ j`,
`∑_i 1 / C(|A_i|+|B_i|, |A_i|) ≤ 1`.

**Lean** (`RequestProject/SetPairs/WeightedBollobas.lean`):
```lean
theorem SetPairs.weighted_bollobas
    [Fintype α] [DecidableEq α] [Fintype ι] [DecidableEq ι]
    (A B : ι → Finset α)
    (hdiag : ∀ i, Disjoint (A i) (B i))
    (hcross : ∀ ⦃i j⦄, i ≠ j → (A i ∩ B j).Nonempty) :
    ∑ i, ((Nat.choose ((A i).card + (B i).card) (A i).card : ℚ)⁻¹) ≤ 1
```

## 2. Uniform Bollobás theorem

**Informal.** If additionally `|A_i| = a`, `|B_i| = b` for all `i`, then
`|ι| ≤ C(a+b, a)`.

**Lean** (`RequestProject/SetPairs/Uniform.lean`):
```lean
theorem SetPairs.uniform_bollobas {a b : ℕ}
    (A B : ι → Finset α)
    (hcardA : ∀ i, (A i).card = a) (hcardB : ∀ i, (B i).card = b)
    (hdiag : ∀ i, Disjoint (A i) (B i))
    (hcross : ∀ ⦃i j⦄, i ≠ j → (A i ∩ B j).Nonempty) :
    Fintype.card ι ≤ Nat.choose (a + b) a
```

## 3. Lovász–Frankl skew two-families theorem for subspaces

**Informal.** Let `dim V = a+b`, `U_i, W_i ≤ V` with `dim U_i = a`, `dim W_i = b`,
`U_i ∩ W_i = 0`, and `U_i ∩ W_j ≠ 0` for `i < j`. Then `m ≤ C(a+b, a)`.

**Lean** (`RequestProject/LinearAlgebra/TwoFamiliesSubspaces.lean`):
```lean
theorem TwoFamilies.lovasz_frankl_subspaces [FiniteDimensional K V]
    (a b m : ℕ) (hdimV : Module.finrank K V = a + b)
    (U W : Fin m → Submodule K V)
    (hdimU : ∀ i, Module.finrank K (U i) = a)
    (hdimW : ∀ i, Module.finrank K (W i) = b)
    (hdiag : ∀ i, U i ⊓ W i = ⊥)
    (hcross : ∀ ⦃i j⦄, i < j → U i ⊓ W j ≠ ⊥) :
    m ≤ Nat.choose (a + b) a
```

## 4. Moment-curve general-position theorem

**Informal.** For an injective `t : α → ℚ`, any set of at most `d` distinct
moment-curve vectors `v_x = (1, t_x, …, t_x^{d-1})` is linearly independent.

**Lean** (`RequestProject/LinearAlgebra/MomentCurve.lean`):
```lean
theorem GeneralPosition.momentCurve_linearIndependent
    [Fintype α] [DecidableEq α]
    (t : α → ℚ) (ht : Function.Injective t)
    (s : Finset α) (hs : s.card ≤ d) :
    LinearIndependent ℚ (fun x : s => momentCurve d t x)
```

## 5. Frankl–Kalai skew set-pairs theorem

**Informal.** For `A_i, B_i ⊆ α` (finite `α`) with `|A_i| = a`, `|B_i| = b`,
`A_i ∩ B_i = ∅`, and `A_i ∩ B_j ≠ ∅` for `i < j`, we have `m ≤ C(a+b, a)`.

**Lean** (`RequestProject/SkewSetPairs.lean`):
```lean
theorem SetPairs.frankl_kalai_skew [Fintype α] [DecidableEq α]
    (A B : Fin m → Finset α)
    (hcardA : ∀ i, (A i).card = a) (hcardB : ∀ i, (B i).card = b)
    (hdiag : ∀ i, Disjoint (A i) (B i))
    (hcross : ∀ ⦃i j⦄, i < j → (A i ∩ B j).Nonempty) :
    m ≤ Nat.choose (a + b) a
```

## Key supporting declarations

| Informal | Lean | File |
|---|---|---|
| #order enumerations = n! | `SetPairs.card_orderEnumerations` | `SetPairs/PermutationOrders.lean` |
| exact event count · C = n! | `SetPairs.card_separationEvent_mul_choose` | `SetPairs/SeparationEvents.lean` |
| separation events pairwise disjoint | `SetPairs.separationEvents_pairwiseDisjoint` | `SetPairs/WeightedBollobas.lean` |
| sharpness construction | `SetPairs.uniform_bollobas_sharp` | `SetPairs/Uniform.lean` |
| triangular independence | `LinearIndependent.of_upperTriangular_maps` | `LinearAlgebra/TriangularIndependence.lean` |
| decomposable vanishing | `ExteriorAlgebra.ιMulti_eq_zero_of_linearDependent` | `LinearAlgebra/ExteriorDecomposable.lean` |
| decomposable nonvanishing | `ExteriorAlgebra.ιMulti_ne_zero_of_linearIndependent` | `LinearAlgebra/ExteriorDecomposable.lean` |
| exterior concatenation | `ExteriorAlgebra.ιMulti_mul_ιMulti` | `LinearAlgebra/ExteriorMultiplication.lean` |
| moment-curve span dimension | `GeneralPosition.finrank_spanMomentCurve` | `LinearAlgebra/MomentCurve.lean` |
| disjoint spans trivial intersection | `GeneralPosition.inf_spanMomentCurve_eq_bot` | `LinearAlgebra/MomentCurve.lean` |
| intersecting spans nontrivial | `GeneralPosition.inf_spanMomentCurve_ne_bot` | `LinearAlgebra/MomentCurve.lean` |
