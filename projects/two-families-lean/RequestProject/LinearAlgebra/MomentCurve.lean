import Mathlib

/-!
# Moment-curve general-position construction

For a finite type `α` with an injective label `t : α → ℚ`, the *moment-curve
vector* of `x` is `v x = (1, t x, t x ^ 2, …, t x ^ (d-1)) ∈ ℚ^d`.

Any family of at most `d` distinct moment-curve vectors is linearly independent
(Vandermonde), so the moment curve realises `α` in general position in `ℚ^d`.
This is the bridge from finite set systems to subspace configurations.
-/

open scoped BigOperators
open Submodule

namespace GeneralPosition

variable {α : Type*} {d : ℕ}

/-- The moment-curve vector `(1, t x, t x ^ 2, …, t x ^ (d-1)) ∈ Fin d → ℚ`. -/
def momentCurve (d : ℕ) (t : α → ℚ) (x : α) : Fin d → ℚ :=
  fun r => t x ^ (r : ℕ)

@[simp] lemma momentCurve_apply (t : α → ℚ) (x : α) (r : Fin d) :
    momentCurve d t x r = t x ^ (r : ℕ) := rfl

/-- Every moment-curve vector is nonzero: its zeroth coordinate is `1`
(requires `d ≠ 0`). -/
theorem momentCurve_ne_zero (t : α → ℚ) (x : α) (hd : d ≠ 0) :
    momentCurve d t x ≠ 0 := by
  intro h
  have h0 : momentCurve d t x ⟨0, Nat.pos_of_ne_zero hd⟩ = 0 := by rw [h]; rfl
  simp [momentCurve] at h0

/-- **Main general-position theorem.** Any family of at most `d` distinct moment-curve
vectors is linearly independent. Proved via the Vandermonde determinant. -/
theorem momentCurve_linearIndependent [Fintype α] [DecidableEq α]
    (t : α → ℚ) (ht : Function.Injective t)
    (s : Finset α) (hs : s.card ≤ d) :
    LinearIndependent ℚ (fun x : s => momentCurve d t x) := by
  classical
  rw [Fintype.linearIndependent_iff]
  intro u hu i
  -- For each coordinate r, we have ∑ i, u i * (t i)^r = 0
  have hcoords : ∀ r : Fin d, ∑ j : ↥s, u j * (t j : ℚ) ^ (r : ℕ) = 0 := by
    intro r
    have := congrFun hu r
    simp [momentCurve_apply] at this
    exact this
  -- For any polynomial p of degree < d, ∑ j, u j * p(t j) = 0
  have hpoly : ∀ p : Polynomial ℚ, p.natDegree < d → ∑ j : ↥s, u j * p.eval (t j) = 0 := by
    intro p hp
    calc ∑ j : ↥s, u j * p.eval (t j)
        = ∑ j : ↥s, u j * ∑ r ∈ Finset.range (p.natDegree + 1), p.coeff r * (t j) ^ r := by
            congr 1; ext j; rw [Polynomial.eval_eq_sum_range]
      _ = ∑ r ∈ Finset.range (p.natDegree + 1), ∑ j : ↥s, u j * p.coeff r * (t j) ^ r := by
            rw [Finset.sum_comm]
            congr 1; ext j; rw [Finset.mul_sum]
            congr 1; ext r; ring
      _ = ∑ r ∈ Finset.range (p.natDegree + 1), p.coeff r * ∑ j : ↥s, u j * (t j) ^ r := by
            congr 1; ext r; rw [Finset.mul_sum]; congr 1; ext j; ring
      _ = 0 := by
            apply Finset.sum_eq_zero
            intro r hr
            rw [mul_eq_zero]
            right
            have hr' : r < d := by linarith [hp, Finset.mem_range.mp hr]
            simpa using hcoords ⟨r, hr'⟩
  -- Consider the polynomial p(x) = ∏_{j ∈ s, j ≠ i} (x - t j)
  let p : Polynomial ℚ := Finset.prod (Finset.univ.erase i) (fun j => Polynomial.X - Polynomial.C (t j))
  -- The degree of p is s.card - 1 < d
  have hp_deg : p.natDegree < d := by
    simp only [p]
    rw [Polynomial.natDegree_prod]
    · simp only [Polynomial.natDegree_X_sub_C]
      simp only [Finset.sum_const, nsmul_one]
      have hcard : (Finset.univ.erase i).card = s.card - 1 := by
        rw [Finset.card_erase_of_mem (Finset.mem_univ i)]
        simp only [Finset.card_univ, Fintype.card_coe]
      rw [hcard]
      have hpos : s.card ≥ 1 := Finset.card_pos.mpr ⟨i, i.prop⟩
      have : s.card - 1 < s.card := Nat.sub_lt (by linarith) (by linarith)
      linarith
    · intro j _
      exact Polynomial.X_sub_C_ne_zero _
  -- For j ≠ i, p.eval (t j) = 0
  have hp_eval_ne : ∀ j : ↥s, j ≠ i → p.eval (t j) = 0 := by
    intro j hj
    simp only [p, Polynomial.eval_prod]
    apply Finset.prod_eq_zero (Finset.mem_erase_of_ne_of_mem hj (Finset.mem_univ j))
    simp
  -- For i, p.eval (t i) ≠ 0
  have hp_eval_i : p.eval (t i) ≠ 0 := by
    simp only [p, Polynomial.eval_prod]
    apply Finset.prod_ne_zero_iff.mpr
    intro j hj
    simp only [Polynomial.eval_sub, Polynomial.eval_X, Polynomial.eval_C]
    have hne : j ≠ i := Finset.ne_of_mem_erase hj
    exact sub_ne_zero.mpr (ht.ne (Ne.symm (by simpa using hne)))
  -- From hpoly: ∑ j, u j * p.eval (t j) = 0
  have hsum := hpoly p hp_deg
  -- This simplifies to u i * p.eval (t i) = 0
  have hsingle : u i * p.eval (t i) = 0 := by
    rw [← hsum]
    rw [Finset.sum_eq_single i (fun j _ hj => by rw [hp_eval_ne j hj, mul_zero]) (by simp)]
  -- Therefore u i = 0
  exact mul_eq_zero.mp hsingle |> Or.resolve_right <| hp_eval_i

/-- The span of the moment-curve vectors of a finite set `S`. -/
noncomputable def spanMomentCurve (d : ℕ) (t : α → ℚ) (S : Finset α) :
    Submodule ℚ (Fin d → ℚ) :=
  Submodule.span ℚ (Set.range (fun x : S => momentCurve d t x))

/-- If `|S| ≤ d`, the span of the moment-curve vectors of `S` has dimension exactly `|S|`. -/
theorem finrank_spanMomentCurve [Fintype α] [DecidableEq α]
    (t : α → ℚ) (ht : Function.Injective t) (S : Finset α) (hS : S.card ≤ d) :
    Module.finrank ℚ (spanMomentCurve d t S) = S.card := by
  unfold spanMomentCurve
  rw [finrank_span_eq_card (momentCurve_linearIndependent t ht S hS)]
  simp

/-- Disjoint sets whose sizes fit within `d` give spans with trivial intersection. -/
theorem inf_spanMomentCurve_eq_bot [Fintype α] [DecidableEq α]
    (t : α → ℚ) (ht : Function.Injective t) (S T : Finset α)
    (hdisj : Disjoint S T) (hcard : S.card + T.card ≤ d) :
    spanMomentCurve d t S ⊓ spanMomentCurve d t T = ⊥ := by
  classical
  set v : ↥(S ∪ T) → (Fin d → ℚ) := fun x => momentCurve d t (x : α) with hv
  have hcardU : (S ∪ T).card ≤ d := by
    rw [Finset.card_union_of_disjoint hdisj]; exact hcard
  have hLI : LinearIndependent ℚ v := momentCurve_linearIndependent t ht (S ∪ T) hcardU
  set sset : Set ↥(S ∪ T) := {x | (x : α) ∈ S} with hsset
  set tset : Set ↥(S ∪ T) := {x | (x : α) ∈ T} with htset
  have hdisjSets : Disjoint sset tset := by
    rw [Set.disjoint_left]
    rintro x hx hx'
    exact (Finset.disjoint_left.mp hdisj) hx hx'
  have hkey := hLI.disjoint_span_image (s := sset) (t := tset) hdisjSets
  have hSspan : Submodule.span ℚ (v '' sset) = spanMomentCurve d t S := by
    unfold spanMomentCurve
    congr 1
    ext w
    constructor
    · rintro ⟨x, hx, rfl⟩
      exact ⟨⟨(x:α), hx⟩, rfl⟩
    · rintro ⟨y, rfl⟩
      exact ⟨⟨(y:α), Finset.mem_union_left _ y.2⟩, y.2, rfl⟩
  have hTspan : Submodule.span ℚ (v '' tset) = spanMomentCurve d t T := by
    unfold spanMomentCurve
    congr 1
    ext w
    constructor
    · rintro ⟨x, hx, rfl⟩
      exact ⟨⟨(x:α), hx⟩, rfl⟩
    · rintro ⟨y, rfl⟩
      exact ⟨⟨(y:α), Finset.mem_union_right _ y.2⟩, y.2, rfl⟩
  rw [hSspan, hTspan] at hkey
  rwa [disjoint_iff] at hkey

/-- Intersecting sets give spans with nontrivial intersection: a common element
`x ∈ S ∩ T` gives a nonzero vector in both spans. -/
theorem inf_spanMomentCurve_ne_bot [Fintype α] [DecidableEq α]
    (t : α → ℚ) (S T : Finset α) (hd : d ≠ 0)
    (hST : (S ∩ T).Nonempty) :
    spanMomentCurve d t S ⊓ spanMomentCurve d t T ≠ ⊥ := by
  obtain ⟨x, hx⟩ := hST
  rw [Finset.mem_inter] at hx
  intro hbot
  have hvS : momentCurve d t x ∈ spanMomentCurve d t S :=
    Submodule.subset_span ⟨⟨x, hx.1⟩, rfl⟩
  have hvT : momentCurve d t x ∈ spanMomentCurve d t T :=
    Submodule.subset_span ⟨⟨x, hx.2⟩, rfl⟩
  have hmem : momentCurve d t x ∈ spanMomentCurve d t S ⊓ spanMomentCurve d t T :=
    ⟨hvS, hvT⟩
  rw [hbot, Submodule.mem_bot] at hmem
  exact momentCurve_ne_zero t x hd hmem

end GeneralPosition
