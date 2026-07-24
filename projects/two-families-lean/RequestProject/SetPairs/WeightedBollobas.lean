import Mathlib
import RequestProject.SetPairs.SeparationEvents

/-!
# Bollobás's weighted set-pairs inequality

The main theorem of the permutation-counting route: for diagonally-disjoint,
cross-intersecting set pairs `(A i, B i)`,
`∑ i, 1 / C(|A i| + |B i|, |A i|) ≤ 1`.

Proof: each pair defines a separation event `E i` among the `(card α)!` order
enumerations, with `|E i| = (card α)! / C(|A i|+|B i|, |A i|)` (exact count) and the
`E i` pairwise disjoint.  Summing the disjoint cardinalities gives the bound.
-/

open scoped BigOperators

namespace SetPairs

variable {α : Type*} {ι : Type*} [Fintype α] [DecidableEq α] [Fintype ι] [DecidableEq ι]

/-- The separation events of a diagonally-disjoint, cross-intersecting family are
pairwise disjoint. -/
theorem separationEvents_pairwiseDisjoint
    (A B : ι → Finset α)
    (hcross : ∀ ⦃i j⦄, i ≠ j → (A i ∩ B j).Nonempty) :
    (Set.univ : Set ι).PairwiseDisjoint
      (fun i => separationEvent (A i) (B i)) := by
  intro i _ j _ hij
  exact separationEvents_disjoint (hcross hij) (hcross (Ne.symm hij))

/-- **Bollobás's weighted set-pairs inequality.** -/
theorem weighted_bollobas
    (A B : ι → Finset α)
    (hdiag : ∀ i, Disjoint (A i) (B i))
    (hcross : ∀ ⦃i j⦄, i ≠ j → (A i ∩ B j).Nonempty) :
    ∑ i, ((Nat.choose ((A i).card + (B i).card) (A i).card : ℚ)⁻¹) ≤ 1 := by
  classical
  set n := Fintype.card α with hn
  have hnpos : (0 : ℚ) < (Nat.factorial n : ℚ) := by
    exact_mod_cast Nat.factorial_pos n
  set E : ι → Finset (OrderEnumeration α) := fun i => separationEvent (A i) (B i) with hE
  -- Each reciprocal equals |E i| / n!.
  have hterm : ∀ i, ((Nat.choose ((A i).card + (B i).card) (A i).card : ℚ))⁻¹
      = ((E i).card : ℚ) / (Nat.factorial n : ℚ) := by
    intro i
    have hc := card_separationEvent_mul_choose (A i) (B i) (hdiag i)
    have hcq : ((E i).card : ℚ) * (Nat.choose ((A i).card + (B i).card) (A i).card : ℚ)
        = (Nat.factorial n : ℚ) := by exact_mod_cast hc
    have hchoose : (0 : ℚ) < (Nat.choose ((A i).card + (B i).card) (A i).card : ℚ) := by
      exact_mod_cast Nat.choose_pos (Nat.le_add_right _ _)
    field_simp
    linarith [hcq]
  -- The events are pairwise disjoint, so their total size is at most n!.
  have hdisj := separationEvents_pairwiseDisjoint A B hcross
  have hbu : (Finset.univ.biUnion E).card = ∑ i, (E i).card := by
    rw [Finset.card_biUnion]
    intro i _ j _ hij
    exact hdisj (Set.mem_univ i) (Set.mem_univ j) hij
  have hle : ∑ i, (E i).card ≤ Nat.factorial n := by
    rw [← hbu]
    calc (Finset.univ.biUnion E).card
        ≤ Fintype.card (OrderEnumeration α) := Finset.card_le_univ _
      _ = Nat.factorial n := card_orderEnumerations
  calc ∑ i, ((Nat.choose ((A i).card + (B i).card) (A i).card : ℚ))⁻¹
      = ∑ i, ((E i).card : ℚ) / (Nat.factorial n : ℚ) := by
        exact Finset.sum_congr rfl (fun i _ => hterm i)
    _ = (∑ i, ((E i).card : ℚ)) / (Nat.factorial n : ℚ) := by rw [← Finset.sum_div]
    _ ≤ 1 := by
        rw [div_le_one hnpos]
        have : (∑ i, ((E i).card : ℚ)) = ((∑ i, (E i).card : ℕ) : ℚ) := by
          push_cast; rfl
        rw [this]
        exact_mod_cast hle

end SetPairs
