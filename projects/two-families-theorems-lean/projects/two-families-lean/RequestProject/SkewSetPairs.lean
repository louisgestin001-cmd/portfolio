import Mathlib
import RequestProject.SetPairs.Basic
import RequestProject.LinearAlgebra.MomentCurve
import RequestProject.LinearAlgebra.TwoFamiliesSubspaces

/-!
# Frankl–Kalai skew set-pairs theorem

For skew cross-intersecting, diagonally-disjoint set pairs with uniform sizes
`|A i| = a`, `|B i| = b`, we have `m ≤ C(a+b, a)`.

The proof realises the ground type in general position on the moment curve over `ℚ`
(dimension `d = a + b`), turning each `A i`, `B i` into subspaces `U i`, `W i`, and
applies the Lovász–Frankl subspace theorem.
-/

open scoped BigOperators
open GeneralPosition TwoFamilies

namespace SetPairs

variable {α : Type*} [Fintype α] [DecidableEq α] {m a b : ℕ}

/-- **Frankl–Kalai skew two-families theorem for finite sets.** -/
theorem frankl_kalai_skew
    (A B : Fin m → Finset α)
    (hcardA : ∀ i, (A i).card = a)
    (hcardB : ∀ i, (B i).card = b)
    (hdiag : ∀ i, Disjoint (A i) (B i))
    (hcross : ∀ ⦃i j⦄, i < j → (A i ∩ B j).Nonempty) :
    m ≤ Nat.choose (a + b) a := by
  classical
  set d := a + b with hd_def
  -- An injective label of the ground type into ℚ.
  have ht : Function.Injective (fun x : α => ((Fintype.equivFin α x : ℕ) : ℚ)) := by
    intro x y hxy
    simp only [Nat.cast_inj] at hxy
    exact (Fintype.equivFin α).injective (Fin.val_injective hxy)
  set t : α → ℚ := fun x => ((Fintype.equivFin α x : ℕ) : ℚ) with ht_def
  -- Realise the sets as moment-curve spans in ℚ^d.
  set U : Fin m → Submodule ℚ (Fin d → ℚ) :=
    fun i => GeneralPosition.spanMomentCurve d t (A i) with hU
  set W : Fin m → Submodule ℚ (Fin d → ℚ) :=
    fun i => GeneralPosition.spanMomentCurve d t (B i) with hW
  refine TwoFamilies.lovasz_frankl_subspaces (K := ℚ) (V := Fin d → ℚ) a b m ?_ U W ?_ ?_ ?_ ?_
  · rw [Module.finrank_fin_fun]
  · intro i
    rw [hU, GeneralPosition.finrank_spanMomentCurve t ht (A i) (by rw [hcardA i]; omega),
      hcardA i]
  · intro i
    rw [hW, GeneralPosition.finrank_spanMomentCurve t ht (B i) (by rw [hcardB i]; omega),
      hcardB i]
  · intro i
    exact GeneralPosition.inf_spanMomentCurve_eq_bot t ht (A i) (B i) (hdiag i)
      (by rw [hcardA i, hcardB i])
  · intro i j hij
    have hne := hcross hij
    by_cases hd0 : d = 0
    · exfalso
      have ha : a = 0 := by omega
      have hAi : A i = ∅ := by rw [← Finset.card_eq_zero, hcardA i, ha]
      rw [hAi] at hne
      simp at hne
    · exact GeneralPosition.inf_spanMomentCurve_ne_bot t (A i) (B j) hd0 hne

end SetPairs
