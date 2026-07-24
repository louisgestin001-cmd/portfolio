import Mathlib

/-!
# Set-pairs: basic predicates and API

This file develops the reusable predicates for families of set pairs used in the
Bollobás–Lovász–Frankl two-families theorems, together with basic symmetry,
restriction, and reindexing lemmas.

A *set-pair family* is a pair of functions `A B : ι → Finset α` assigning to each
index `i` two finite subsets `A i`, `B i` of a ground type `α`.
-/

open scoped BigOperators

namespace SetPairs

variable {α : Type*} {ι : Type*} {m : ℕ} [DecidableEq α]

/-- The pairs are *diagonally disjoint* if `A i` and `B i` are disjoint for every `i`. -/
def DiagonallyDisjoint (A B : ι → Finset α) : Prop :=
  ∀ i, Disjoint (A i) (B i)

/-- The pairs are *cross-intersecting* if `A i ∩ B j` is nonempty for all `i ≠ j`. -/
def CrossIntersecting (A B : ι → Finset α) : Prop :=
  ∀ ⦃i j⦄, i ≠ j → (A i ∩ B j).Nonempty

/-- The pairs are *skew cross-intersecting* if `A i ∩ B j` is nonempty whenever `i < j`
(with respect to the order on the index type `Fin m`). -/
def SkewCrossIntersecting (A B : Fin m → Finset α) : Prop :=
  ∀ ⦃i j⦄, i < j → (A i ∩ B j).Nonempty

/-- Cross-intersection is symmetric in the two families up to swapping the two arguments. -/
theorem CrossIntersecting.symm {A B : ι → Finset α}
    (h : CrossIntersecting A B) : CrossIntersecting B A := by
  intro i j hij
  have := h (Ne.symm hij)
  rwa [Finset.inter_comm] at this

/-- Cross-intersecting implies skew cross-intersecting (the diagonal is excluded by `i < j`). -/
theorem CrossIntersecting.toSkew {A B : Fin m → Finset α}
    (h : CrossIntersecting A B) : SkewCrossIntersecting A B :=
  fun _ _ hij => h (ne_of_lt hij)

omit [DecidableEq α] in
/-- Restricting a diagonally-disjoint family to a sub-index set stays diagonally disjoint. -/
theorem DiagonallyDisjoint.comp {ι' : Type*} {A B : ι → Finset α}
    (h : DiagonallyDisjoint A B) (f : ι' → ι) :
    DiagonallyDisjoint (A ∘ f) (B ∘ f) :=
  fun i => h (f i)

/-- Reindexing along an injective map preserves cross-intersection. -/
theorem CrossIntersecting.comp_injective {ι' : Type*} {A B : ι → Finset α}
    (h : CrossIntersecting A B) {f : ι' → ι} (hf : Function.Injective f) :
    CrossIntersecting (A ∘ f) (B ∘ f) :=
  fun _ _ hij => h (fun he => hij (hf he))

end SetPairs
