import Mathlib
import RequestProject.SetPairs.WeightedBollobas

/-!
# Uniform Bollobás corollary and sharpness

If every `A i` has size `a` and every `B i` has size `b`, the weighted inequality
gives `|ι| ≤ C(a+b, a)`.  The canonical complement family on `Fin (a+b)` (all
`a`-subsets `S` with `A_S = S`, `B_S = Sᶜ`) attains this bound.
-/

open scoped BigOperators

namespace SetPairs

variable {α : Type*} {ι : Type*} [Fintype α] [DecidableEq α] [Fintype ι] [DecidableEq ι]

/-- **Uniform Bollobás theorem.** For a diagonally-disjoint, cross-intersecting family
with `|A i| = a` and `|B i| = b`, we have `|ι| ≤ C(a+b, a)`. -/
theorem uniform_bollobas {a b : ℕ}
    (A B : ι → Finset α)
    (hcardA : ∀ i, (A i).card = a)
    (hcardB : ∀ i, (B i).card = b)
    (hdiag : ∀ i, Disjoint (A i) (B i))
    (hcross : ∀ ⦃i j⦄, i ≠ j → (A i ∩ B j).Nonempty) :
    Fintype.card ι ≤ Nat.choose (a + b) a := by
  have hw := weighted_bollobas A B hdiag hcross
  simp_rw [hcardA, hcardB, Finset.sum_const, Finset.card_univ, nsmul_eq_mul] at hw
  have hC : (0 : ℚ) < (Nat.choose (a + b) a : ℚ) := by
    exact_mod_cast Nat.choose_pos (Nat.le_add_right a b)
  rw [← div_eq_mul_inv, div_le_one hC] at hw
  exact_mod_cast hw

/-! ## Sharpness: the canonical complement family -/

namespace Sharp

variable (a b : ℕ)

/-- Index type of the sharp construction: `a`-subsets of `Fin (a+b)`. -/
abbrev Index (a b : ℕ) := {S : Finset (Fin (a + b)) // S.card = a}

instance : Fintype (Index a b) := Subtype.fintype _

/-- `A_S = S`. -/
def famA (S : Index a b) : Finset (Fin (a + b)) := S.1

/-- `B_S = Sᶜ`. -/
def famB (S : Index a b) : Finset (Fin (a + b)) := S.1ᶜ

end Sharp

/-- **Sharpness of the uniform bound.** The canonical complement family on `Fin (a+b)`
is diagonally disjoint, cross-intersecting, has `|A_S| = a`, `|B_S| = b`, and exactly
`C(a+b, a)` members. -/
theorem uniform_bollobas_sharp (a b : ℕ) :
    (∀ S, Disjoint (Sharp.famA a b S) (Sharp.famB a b S)) ∧
    (∀ ⦃S T⦄, S ≠ T → (Sharp.famA a b S ∩ Sharp.famB a b T).Nonempty) ∧
    (∀ S, (Sharp.famA a b S).card = a) ∧
    (∀ S, (Sharp.famB a b S).card = b) ∧
    Fintype.card (Sharp.Index a b) = Nat.choose (a + b) a := by
  refine ⟨?_, ?_, ?_, ?_, ?_⟩
  -- Disjoint: S ∩ Sᶜ = ∅
  · intro S
    exact disjoint_compl_right
  -- Cross-intersecting: S ≠ T → (S ∩ Tᶜ).Nonempty
  · intro S T hne
    simp [Sharp.famA, Sharp.famB]
    have hne' : S.1 ≠ T.1 := by
      intro heq
      apply hne
      exact Subtype.ext heq
    have : ¬ S.1 ⊆ T.1 := by
      intro hsub
      apply hne'
      exact Finset.eq_of_subset_of_card_le hsub (by simp [S.2, T.2])
    rw [Finset.not_subset] at this
    obtain ⟨x, hxS, hxT⟩ := this
    exact Finset.nonempty_of_ne_empty (Finset.ne_empty_of_mem (Finset.mem_inter.mpr ⟨hxS, Finset.mem_compl.mpr hxT⟩))
  -- |famA S| = a
  · intro S
    exact S.2
  -- |famB S| = b
  · intro S
    simp [Sharp.famB]
    have : S.1.card + S.1ᶜ.card = Fintype.card (Fin (a + b)) := Finset.card_add_card_compl S.1
    rw [S.2] at this
    simp [Fintype.card_fin] at this
    omega
  -- Cardinality
  · simp [Sharp.Index]

end SetPairs
