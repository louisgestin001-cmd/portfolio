import Mathlib
import RequestProject.SetPairs.PermutationOrders

/-!
# Separation events and their exact cardinalities

Given a total order (order enumeration) `e : α ≃ Fin (card α)`, the pair `(A, B)`
is *separated* by `e` if every element of `A` occurs before every element of `B`.

We prove:
* the exact count `|separationEvent A B| · C(|A|+|B|, |A|) = (card α)!`, via an
  explicit ordering-factorization equivalence;
* separation events for cross-intersecting diagonally-disjoint pairs are pairwise
  disjoint.

## The counting proof

Write `n = card α`, `a = |A|`, `b = |B|`, `S = A ∪ B`, `k = a + b`.  The proof factors
a global separating ordering into three independent pieces:

* the `k`-element set `P ⊆ Fin n` of positions occupied by `S` (contributing `C(n, k)`);
* the relative order of `S`, in which `A` precedes `B` (contributing `a!·b!`);
* the relative order of `Sᶜ` (contributing `(n-k)!`).

Concretely:

* `card_separates_full` : with `A ∪ B = univ`, the separating orderings biject with
  `(A ≃ Fin a) × (B ≃ Fin b)`, giving the count `a!·b!` (proved by an order-statistics
  argument and two explicit injections).
* `card_separates_toP` : transports `card_separates_full` from `Fin k` to an arbitrary
  ordered `k`-set `P`, giving the relative-order-of-`S` count `a!·b!`.
* `fiber_card_eq` : for a fixed position set `P`, the orderings whose `S`-image is `P`
  biject with `(relative order of S) × (Sᶜ ≃ Pᶜ)`.
* `card_separationEvent_eq` : sums the fibre counts over the `C(n, k)` position sets.
* `card_separationEvent_mul_choose` : the clean factorial identity, via
  `Nat.choose_mul_factorial_mul_factorial`.
-/

open scoped BigOperators

namespace SetPairs

open Finset

variable {α : Type*} [Fintype α] [DecidableEq α]

/-- `e` *separates* `(A, B)` if every element of `A` precedes every element of `B`. -/
def Separates (e : OrderEnumeration α) (A B : Finset α) : Prop :=
  ∀ ⦃x⦄, x ∈ A → ∀ ⦃y⦄, y ∈ B → e x < e y

instance (e : OrderEnumeration α) (A B : Finset α) : Decidable (Separates e A B) := by
  unfold Separates; infer_instance

/-- The separation event of `(A, B)`: the set of order enumerations separating it. -/
noncomputable def separationEvent (A B : Finset α) : Finset (OrderEnumeration α) :=
  Finset.univ.filter (fun e => Separates e A B)

@[simp] lemma mem_separationEvent {A B : Finset α} {e : OrderEnumeration α} :
    e ∈ separationEvent A B ↔ Separates e A B := by
  simp [separationEvent]

/-! ### Order-statistics facts for the full-support case -/

/-- If `A ∪ B` is everything and `e` separates `(A, B)`, then every element of `A` gets a
position strictly below `|A|`. -/
theorem separates_val_lt (A B : Finset α) (hcov : A ∪ B = univ)
    (e : OrderEnumeration α) (hsep : Separates e A B) {x : α} (hx : x ∈ A) :
    (e x : ℕ) < A.card := by
  have hsub : (univ.filter (fun i : Fin (Fintype.card α) => i ≤ e x)) ⊆ A.image e := by
    intro i hi
    simp only [mem_filter, mem_univ, true_and] at hi
    rw [mem_image]
    refine ⟨e.symm i, ?_, by simp⟩
    by_contra hnot
    have hmem : e.symm i ∈ A ∪ B := hcov ▸ mem_univ _
    have hiB : e.symm i ∈ B := (mem_union.1 hmem).resolve_left hnot
    have hlt := hsep hx hiB
    simp only [Equiv.apply_symm_apply] at hlt
    exact absurd hi (not_le.2 hlt)
  have h1 : (univ.filter (fun i : Fin (Fintype.card α) => i ≤ e x)).card = (e x : ℕ) + 1 := by
    have : (univ.filter (fun i : Fin (Fintype.card α) => i ≤ e x)) = Finset.Iic (e x) := by
      ext i; simp [mem_Iic]
    rw [this]; simp [Fin.card_Iic]
  have h2 : (A.image e).card = A.card := card_image_of_injective _ e.injective
  have h3 := card_le_card hsub
  omega

/-- If `e` separates `(A, B)`, then every element of `B` gets a position at least `|A|`. -/
theorem card_le_separates_val (A B : Finset α)
    (e : OrderEnumeration α) (hsep : Separates e A B) {y : α} (hy : y ∈ B) :
    A.card ≤ (e y : ℕ) := by
  have hsub : A.image e ⊆ (univ.filter (fun i : Fin (Fintype.card α) => i < e y)) := by
    intro i hi
    rw [mem_image] at hi
    obtain ⟨w, hw, rfl⟩ := hi
    simp only [mem_filter, mem_univ, true_and]
    exact hsep hw hy
  have h2 : (A.image e).card = A.card := card_image_of_injective _ e.injective
  have h1 : (univ.filter (fun i : Fin (Fintype.card α) => i < e y)).card = (e y : ℕ) := by
    have : (univ.filter (fun i : Fin (Fintype.card α) => i < e y)) = Finset.Iio (e y) := by
      ext i; simp [mem_Iio]
    rw [this]; simp [Fin.card_Iio]
  have h3 := card_le_card hsub
  omega

/-! ### Full-support case: `A ∪ B = univ` -/

/-- **Full-support count.** If `A` and `B` are disjoint with `A ∪ B = univ`, the number of
order enumerations separating `(A, B)` is `|A|! · |B|!`.  Proved by exhibiting mutually
inverse injections to and from `(A ≃ Fin |A|) × (B ≃ Fin |B|)`. -/
theorem card_separates_full (A B : Finset α) (hdisj : Disjoint A B) (hcov : A ∪ B = univ) :
    Fintype.card {e : OrderEnumeration α // Separates e A B}
      = A.card.factorial * B.card.factorial := by
  set n := Fintype.card α with hn
  set a := A.card with ha
  set b := B.card with hb
  have hnab : n = a + b := by
    rw [hn, ← card_univ, ← hcov, card_union_of_disjoint hdisj]
  have hmemB : ∀ x, x ∉ A → x ∈ B := by
    intro x hx
    have : x ∈ A ∪ B := hcov ▸ mem_univ _
    exact (mem_union.1 this).resolve_left hx
  have hAB : ∀ y, y ∈ B → y ∉ A := fun y hy h => Finset.disjoint_left.1 hdisj h hy
  let SepT := {e : α ≃ Fin n // Separates e A B}
  let Tgt := (↥A ≃ Fin a) × (↥B ≃ Fin b)
  have hcardA : Fintype.card ↥A = a := by simp [ha]
  have hcardB : Fintype.card ↥B = b := by simp [hb]
  let fA : SepT → (↥A ≃ Fin a) := fun e =>
    Equiv.ofBijective (fun x : ↥A => (⟨(e.1 x.1 : ℕ), by
        have := separates_val_lt A B hcov e.1 e.2 x.2; simpa [ha] using this⟩ : Fin a)) (by
      rw [Fintype.bijective_iff_injective_and_card]
      refine ⟨?_, by simp [hcardA]⟩
      intro x y hxy
      simp only [Fin.mk.injEq] at hxy
      exact Subtype.ext (e.1.injective (Fin.ext hxy)))
  let fB : SepT → (↥B ≃ Fin b) := fun e =>
    Equiv.ofBijective (fun x : ↥B => (⟨(e.1 x.1 : ℕ) - a, by
        have h1 := card_le_separates_val A B e.1 e.2 x.2
        have h2 : (e.1 x.1 : ℕ) < n := (e.1 x.1).2
        omega⟩ : Fin b)) (by
      rw [Fintype.bijective_iff_injective_and_card]
      refine ⟨?_, by simp [hcardB]⟩
      intro x y hxy
      simp only [Fin.mk.injEq] at hxy
      have h1 := card_le_separates_val A B e.1 e.2 x.2
      have h2 := card_le_separates_val A B e.1 e.2 y.2
      exact Subtype.ext (e.1.injective (Fin.ext (by omega))))
  let Φ : SepT → Tgt := fun e => (fA e, fB e)
  have hΦinj : Function.Injective Φ := by
    intro e e' h
    have hA := congrArg Prod.fst h
    have hB := congrArg Prod.snd h
    apply Subtype.ext; apply Equiv.ext; intro x
    by_cases hx : x ∈ A
    · have := DFunLike.congr_fun hA ⟨x, hx⟩
      simp only [Φ, fA, Equiv.ofBijective_apply, Fin.mk.injEq] at this
      exact Fin.ext this
    · have hxB := hmemB x hx
      have h1 := card_le_separates_val A B e.1 e.2 hxB
      have h2 := card_le_separates_val A B e'.1 e'.2 hxB
      have := DFunLike.congr_fun hB ⟨x, hxB⟩
      simp only [Φ, fB, Equiv.ofBijective_apply, Fin.mk.injEq] at this
      exact Fin.ext (by omega)
  let g : Tgt → (α → Fin n) := fun p x =>
    if hx : x ∈ A then ⟨(p.1 ⟨x,hx⟩ : ℕ), by have := (p.1 ⟨x,hx⟩).2; omega⟩
    else ⟨a + (p.2 ⟨x, hmemB x hx⟩ : ℕ), by have := (p.2 ⟨x, hmemB x hx⟩).2; omega⟩
  have hginj : ∀ p, Function.Injective (g p) := by
    intro p x y hxy
    simp only [g] at hxy
    by_cases hx : x ∈ A <;> by_cases hy : y ∈ A
    · rw [dif_pos hx, dif_pos hy] at hxy
      simp only [Fin.mk.injEq] at hxy
      have := p.1.injective (Fin.ext hxy); simpa using congrArg Subtype.val this
    · rw [dif_pos hx, dif_neg hy] at hxy
      exfalso; have := (p.1 ⟨x,hx⟩).2; simp only [Fin.mk.injEq] at hxy; omega
    · rw [dif_neg hx, dif_pos hy] at hxy
      exfalso; have := (p.1 ⟨y,hy⟩).2; simp only [Fin.mk.injEq] at hxy; omega
    · rw [dif_neg hx, dif_neg hy] at hxy
      simp only [Fin.mk.injEq] at hxy
      have := p.2.injective (Fin.ext (by omega : (p.2 ⟨x,hmemB x hx⟩:ℕ) = (p.2 ⟨y,hmemB y hy⟩:ℕ)))
      simpa using congrArg Subtype.val this
  let mke : Tgt → (α ≃ Fin n) := fun p =>
    Equiv.ofBijective (g p) (by
      rw [Fintype.bijective_iff_injective_and_card]
      exact ⟨hginj p, by simp [hn]⟩)
  have hmke : ∀ p z, (mke p) z = g p z := fun _ _ => rfl
  let Ψ : Tgt → SepT := fun p =>
    ⟨mke p, by
      intro x hx y hy
      have hyA := hAB y hy
      rw [hmke, hmke]
      simp only [g, dif_pos hx, dif_neg hyA]
      exact Fin.mk_lt_mk.mpr (by have := (p.1 ⟨x,hx⟩).2; omega)⟩
  have hΨinj : Function.Injective Ψ := by
    intro p p' h
    have hgg : ∀ z, g p z = g p' z := by
      intro z
      have := DFunLike.congr_fun (Subtype.ext_iff.1 h) z
      rw [hmke, hmke] at this; exact this
    apply Prod.ext
    · apply Equiv.ext; intro x
      have := hgg x.1
      simp only [g, dif_pos x.2, Subtype.coe_eta, Fin.mk.injEq] at this
      exact Fin.ext this
    · apply Equiv.ext; intro y
      have hyA := hAB y.1 y.2
      have := hgg y.1
      simp only [g, dif_neg hyA, Subtype.coe_eta, Fin.mk.injEq] at this
      exact Fin.ext (by omega)
  have h1 : Fintype.card SepT ≤ Fintype.card Tgt := Fintype.card_le_of_injective Φ hΦinj
  have h2 : Fintype.card Tgt ≤ Fintype.card SepT := Fintype.card_le_of_injective Ψ hΨinj
  have heq : Fintype.card SepT = Fintype.card Tgt := le_antisymm h1 h2
  have eA : ↥A ≃ Fin a := Fintype.equivOfCardEq (by simp [hcardA])
  have eB : ↥B ≃ Fin b := Fintype.equivOfCardEq (by simp [hcardB])
  rw [show Fintype.card {e : α ≃ Fin n // Separates e A B} = Fintype.card SepT from rfl, heq]
  simp only [Tgt, Fintype.card_prod, Fintype.card_equiv eA, Fintype.card_equiv eB,
    hcardA, hcardB]

/-! ### Fibre over a fixed position set -/

/-- **Fibre equivalence.** For a fixed `k`-element position set `P`, the separating orderings
whose `S = A ∪ B` image is `P` are counted by (relative orders of `S` separating `A, B`)
times (bijections `Sᶜ ≃ Pᶜ`). -/
theorem fiber_card_eq (A B : Finset α) (hdisj : Disjoint A B)
    (P : Finset (Fin (Fintype.card α))) (hP : P.card = A.card + B.card) :
    Fintype.card {e : OrderEnumeration α // Separates e A B ∧ (A ∪ B).image (⇑e) = P}
      = Fintype.card {f : ↥(A ∪ B) ≃ ↥P //
            ∀ x : ↥(A ∪ B), (x:α) ∈ A → ∀ y : ↥(A ∪ B), (y:α) ∈ B →
              (↑(f x) : Fin (Fintype.card α)) < (↑(f y) : Fin (Fintype.card α))}
        * Fintype.card (↥((A ∪ B)ᶜ) ≃ ↥(Pᶜ)) := by
  classical
  set S := A ∪ B with hSdef
  have hScard : S.card = A.card + B.card := by rw [hSdef, card_union_of_disjoint hdisj]
  have hcardS : Fintype.card ↥S = Fintype.card ↥P := by
    rw [Fintype.card_coe, Fintype.card_coe, hScard, hP]
  have hcardSc : Fintype.card ↥(Sᶜ) = Fintype.card ↥(Pᶜ) := by
    rw [Fintype.card_coe, Fintype.card_coe, card_compl, card_compl, hScard, hP, Fintype.card_fin]
  have hmemP : ∀ (e : α ≃ Fin (Fintype.card α)), S.image (⇑e) = P → ∀ x, (e x ∈ P ↔ x ∈ S) := by
    intro e he x
    constructor
    · intro hx; rw [← he, mem_image] at hx
      obtain ⟨w, hw, hwe⟩ := hx; rwa [e.injective hwe] at hw
    · intro hx; rw [← he, mem_image]; exact ⟨x, hx, rfl⟩
  set FT := {e : α ≃ Fin (Fintype.card α) // Separates e A B ∧ S.image (⇑e) = P} with hFT
  set TgtF := {f : ↥S ≃ ↥P //
      ∀ x : ↥S, (x:α) ∈ A → ∀ y : ↥S, (y:α) ∈ B →
        (↑(f x) : Fin (Fintype.card α)) < (↑(f y) : Fin (Fintype.card α))} with hTgtF
  let mkfS : FT → (↥S ≃ ↥P) := fun e =>
    Equiv.ofBijective (fun x : ↥S => (⟨e.1 x.1, (hmemP e.1 e.2.2 x.1).2 x.2⟩ : ↥P)) (by
      rw [Fintype.bijective_iff_injective_and_card]
      refine ⟨?_, hcardS⟩
      intro x y hxy; simp only [Subtype.mk.injEq] at hxy
      exact Subtype.ext (e.1.injective hxy))
  let mkfSc : FT → (↥(Sᶜ) ≃ ↥(Pᶜ)) := fun e =>
    Equiv.ofBijective (fun x : ↥(Sᶜ) => (⟨e.1 x.1, by
          have hxS : x.1 ∉ S := by have := x.2; rwa [mem_compl] at this
          rw [mem_compl]; exact fun h => hxS ((hmemP e.1 e.2.2 x.1).1 h)⟩ : ↥(Pᶜ))) (by
      rw [Fintype.bijective_iff_injective_and_card]
      refine ⟨?_, hcardSc⟩
      intro x y hxy; simp only [Subtype.mk.injEq] at hxy
      exact Subtype.ext (e.1.injective hxy))
  let Φ : FT → TgtF × (↥(Sᶜ) ≃ ↥(Pᶜ)) :=
    fun e => (⟨mkfS e, by intro x hx y hy; exact e.2.1 hx hy⟩, mkfSc e)
  have hΦinj : Function.Injective Φ := by
    intro e e' h
    have h2 : mkfSc e = mkfSc e' := congrArg Prod.snd h
    have hfS : mkfS e = mkfS e' := congrArg Subtype.val (congrArg Prod.fst h)
    apply Subtype.ext; apply Equiv.ext; intro z
    by_cases hz : z ∈ S
    · have := DFunLike.congr_fun hfS ⟨z, hz⟩
      simpa only [mkfS, Equiv.ofBijective_apply, Subtype.mk.injEq] using this
    · have hzc : z ∈ Sᶜ := by rw [mem_compl]; exact hz
      have := DFunLike.congr_fun h2 ⟨z, hzc⟩
      simpa only [mkfSc, Equiv.ofBijective_apply, Subtype.mk.injEq] using this
  let mkg : (TgtF × (↥(Sᶜ) ≃ ↥(Pᶜ))) → (α → Fin (Fintype.card α)) := fun t z =>
    if hz : z ∈ S then (↑(t.1.1 ⟨z, hz⟩) : Fin (Fintype.card α))
    else (↑(t.2 ⟨z, by rw [mem_compl]; exact hz⟩) : Fin (Fintype.card α))
  have hginj : ∀ t, Function.Injective (mkg t) := by
    intro t z z' hzz
    simp only [mkg] at hzz
    by_cases hz : z ∈ S <;> by_cases hz' : z' ∈ S
    · rw [dif_pos hz, dif_pos hz'] at hzz
      exact congrArg Subtype.val (t.1.1.injective (Subtype.ext hzz))
    · exfalso; rw [dif_pos hz, dif_neg hz'] at hzz
      have h1 : (↑(t.1.1 ⟨z,hz⟩) : Fin (Fintype.card α)) ∈ P := (t.1.1 ⟨z,hz⟩).2
      have h2 : (↑(t.2 ⟨z', by rw [mem_compl]; exact hz'⟩) : Fin (Fintype.card α)) ∉ P := by
        have := (t.2 ⟨z', by rw [mem_compl]; exact hz'⟩).2; rwa [mem_compl] at this
      rw [hzz] at h1; exact h2 h1
    · exfalso; rw [dif_neg hz, dif_pos hz'] at hzz
      have h1 : (↑(t.1.1 ⟨z',hz'⟩) : Fin (Fintype.card α)) ∈ P := (t.1.1 ⟨z',hz'⟩).2
      have h2 : (↑(t.2 ⟨z, by rw [mem_compl]; exact hz⟩) : Fin (Fintype.card α)) ∉ P := by
        have := (t.2 ⟨z, by rw [mem_compl]; exact hz⟩).2; rwa [mem_compl] at this
      rw [← hzz] at h1; exact h2 h1
    · rw [dif_neg hz, dif_neg hz'] at hzz
      exact congrArg Subtype.val (t.2.injective (Subtype.ext hzz))
  let mke0 : (TgtF × (↥(Sᶜ) ≃ ↥(Pᶜ))) → (α ≃ Fin (Fintype.card α)) := fun t =>
    Equiv.ofBijective (mkg t) (by
      rw [Fintype.bijective_iff_injective_and_card]
      exact ⟨hginj t, by simp⟩)
  have hmke0 : ∀ t z, (mke0 t) z = mkg t z := fun _ _ => rfl
  have hsep : ∀ t, Separates (mke0 t) A B := by
    intro t x hx y hy
    have hxS : x ∈ S := by rw [hSdef]; exact mem_union_left _ hx
    have hyS : y ∈ S := by rw [hSdef]; exact mem_union_right _ hy
    rw [hmke0, hmke0]
    simp only [mkg, dif_pos hxS, dif_pos hyS]
    exact t.1.2 ⟨x, hxS⟩ hx ⟨y, hyS⟩ hy
  have himg : ∀ t, S.image (⇑(mke0 t)) = P := by
    intro t
    apply Finset.eq_of_subset_of_card_le
    · intro q hq
      rw [mem_image] at hq
      obtain ⟨z, hz, rfl⟩ := hq
      rw [hmke0]
      simp only [mkg, dif_pos hz]
      exact (t.1.1 ⟨z, hz⟩).2
    · rw [card_image_of_injective _ (mke0 t).injective, hScard, hP]
  let Ψ : (TgtF × (↥(Sᶜ) ≃ ↥(Pᶜ))) → FT := fun t => ⟨mke0 t, ⟨hsep t, himg t⟩⟩
  have hΨinj : Function.Injective Ψ := by
    intro t t' h
    have hgg : ∀ z, mkg t z = mkg t' z := by
      intro z
      have := DFunLike.congr_fun (congrArg Subtype.val h) z
      rw [hmke0, hmke0] at this; exact this
    have hfst : t.1 = t'.1 := by
      apply Subtype.ext; apply Equiv.ext; intro x
      have := hgg x.1
      simp only [mkg, dif_pos x.2] at this
      exact Subtype.ext this
    have hsnd : t.2 = t'.2 := by
      apply Equiv.ext; intro x
      have hxc : x.1 ∉ S := by have := x.2; rwa [mem_compl] at this
      have := hgg x.1
      simp only [mkg, dif_neg hxc, Subtype.coe_eta] at this
      exact Subtype.ext this
    exact Prod.ext hfst hsnd
  have hcardeq : Fintype.card FT = Fintype.card (TgtF × (↥(Sᶜ) ≃ ↥(Pᶜ))) :=
    le_antisymm (Fintype.card_le_of_injective Φ hΦinj) (Fintype.card_le_of_injective Ψ hΨinj)
  rw [hcardeq, Fintype.card_prod]

/-! ### Transport the relative-order count to an arbitrary ordered `k`-set -/

/-- **Relative-order count.** For any ordered `k`-element set `P`, the bijections
`(A ∪ B) ≃ P` that place `A` below `B` number `|A|! · |B|!`.  Proved by transporting
`card_separates_full` along the order isomorphism `P ≃o Fin k`. -/
theorem card_separates_toP (A B : Finset α) (hdisj : Disjoint A B)
    (P : Finset (Fin (Fintype.card α))) (hP : P.card = A.card + B.card) :
    Fintype.card {f : ↥(A ∪ B) ≃ ↥P //
        ∀ x : ↥(A ∪ B), (x:α) ∈ A → ∀ y : ↥(A ∪ B), (y:α) ∈ B →
          (↑(f x) : Fin (Fintype.card α)) < (↑(f y) : Fin (Fintype.card α))}
      = A.card.factorial * B.card.factorial := by
  classical
  set S := A ∪ B with hSdef
  have hScard : S.card = A.card + B.card := by rw [hSdef, card_union_of_disjoint hdisj]
  set A' : Finset ↥S := univ.filter (fun x => (x:α) ∈ A) with hA'
  set B' : Finset ↥S := univ.filter (fun x => (x:α) ∈ B) with hB'
  have hdisj' : Disjoint A' B' := by
    rw [Finset.disjoint_left]; intro x hx hx2
    rw [hA', mem_filter] at hx; rw [hB', mem_filter] at hx2
    exact Finset.disjoint_left.1 hdisj hx.2 hx2.2
  have hcov' : A' ∪ B' = univ := by
    ext x; simp only [mem_union, hA', hB', mem_filter, mem_univ, true_and, iff_true]
    have := x.2; exact mem_union.mp this
  have hcardA' : A'.card = A.card := by
    have himg : A'.image (fun x : ↥S => (x:α)) = A := by
      ext c; simp only [hA', mem_image, mem_filter, mem_univ, true_and]
      constructor
      · rintro ⟨x, hx, rfl⟩; exact hx
      · intro hc; exact ⟨⟨c, mem_union.mpr (Or.inl hc)⟩, hc, rfl⟩
    rw [← himg, card_image_of_injective _ Subtype.coe_injective]
  have hcardB' : B'.card = B.card := by
    have himg : B'.image (fun x : ↥S => (x:α)) = B := by
      ext c; simp only [hB', mem_image, mem_filter, mem_univ, true_and]
      constructor
      · rintro ⟨x, hx, rfl⟩; exact hx
      · intro hc; exact ⟨⟨c, mem_union.mpr (Or.inr hc)⟩, hc, rfl⟩
    rw [← himg, card_image_of_injective _ Subtype.coe_injective]
  have hcardSk : P.card = Fintype.card ↥S := by rw [Fintype.card_coe, hScard, hP]
  let oiso : ↥P ≃o Fin (Fintype.card ↥S) := (P.orderIsoOfFin hcardSk).symm
  let base : (↥S ≃ ↥P) ≃ (↥S ≃ Fin (Fintype.card ↥S)) :=
    Equiv.equivCongr (Equiv.refl _) oiso.toEquiv
  have hbase : ∀ (f : ↥S ≃ ↥P) (x : ↥S), (base f) x = oiso (f x) := fun _ _ => rfl
  let E : {f : ↥S ≃ ↥P //
      ∀ x : ↥S, (x:α) ∈ A → ∀ y : ↥S, (y:α) ∈ B →
        (↑(f x) : Fin (Fintype.card α)) < (↑(f y) : Fin (Fintype.card α))}
      ≃ {h : ↥S ≃ Fin (Fintype.card ↥S) // Separates h A' B'} :=
    Equiv.subtypeEquiv base (by
      intro f
      constructor
      · intro hp x hx y hy
        rw [hbase, hbase, oiso.lt_iff_lt, ← Subtype.coe_lt_coe]
        rw [hA', mem_filter] at hx; rw [hB', mem_filter] at hy
        exact hp x hx.2 y hy.2
      · intro hq x hxA y hyB
        have hx : x ∈ A' := by rw [hA', mem_filter]; exact ⟨mem_univ _, hxA⟩
        have hy : y ∈ B' := by rw [hB', mem_filter]; exact ⟨mem_univ _, hyB⟩
        have h := hq hx hy
        rw [hbase, hbase, oiso.lt_iff_lt, ← Subtype.coe_lt_coe] at h
        exact h)
  rw [Fintype.card_congr E, card_separates_full A' B' hdisj' hcov', hcardA', hcardB']

/-! ### The global count -/

/-- **Core count.** For disjoint `A`, `B`, the number of order enumerations separating
`(A, B)` equals `C(n, a+b) · a! · b! · (n - (a+b))!`, where `n = card α`, `a = |A|`,
`b = |B|`.  Summed over the `C(n, a+b)` choices of position set for `S = A ∪ B`. -/
theorem card_separationEvent_eq (A B : Finset α) (hdisj : Disjoint A B) :
    (separationEvent A B).card
      = (Fintype.card α).choose (A.card + B.card) * (A.card).factorial
          * (B.card).factorial * (Fintype.card α - (A.card + B.card)).factorial := by
  classical
  set S := A ∪ B with hSdef
  have hScard : S.card = A.card + B.card := by rw [hSdef, card_union_of_disjoint hdisj]
  set k := A.card + B.card with hk
  have hmaps : Set.MapsTo (fun e : OrderEnumeration α => S.image ⇑e)
      ↑(separationEvent A B) ↑(powersetCard k (univ : Finset (Fin (Fintype.card α)))) := by
    intro e _
    simp only [Finset.mem_coe, mem_powersetCard]
    exact ⟨subset_univ _, by rw [card_image_of_injective _ e.injective, hScard]⟩
  have hfib : ∀ P ∈ powersetCard k (univ : Finset (Fin (Fintype.card α))),
      ((separationEvent A B).filter
        (fun e : OrderEnumeration α => S.image ⇑e = P)).card
        = A.card.factorial * B.card.factorial * (Fintype.card α - k).factorial := by
    intro P hP
    rw [mem_powersetCard] at hP
    have hPcard : P.card = A.card + B.card := by rw [hP.2]
    have key : ((separationEvent A B).filter
          (fun e : OrderEnumeration α => S.image ⇑e = P)).card
        = Fintype.card {e : OrderEnumeration α // Separates e A B ∧ S.image ⇑e = P} := by
      rw [separationEvent, Finset.filter_filter, Fintype.card_subtype]
    rw [key, fiber_card_eq A B hdisj P hPcard, card_separates_toP A B hdisj P hPcard]
    congr 1
    have hce : Fintype.card ↥(Sᶜ) = Fintype.card ↥(Pᶜ) := by
      rw [Fintype.card_coe, Fintype.card_coe, card_compl, card_compl, hScard, hP.2,
        Fintype.card_fin]
    rw [Fintype.card_equiv (Fintype.equivOfCardEq hce), Fintype.card_coe, card_compl, hScard]
  rw [Finset.card_eq_sum_card_fiberwise hmaps, Finset.sum_congr rfl hfib, Finset.sum_const,
    Finset.card_powersetCard, card_univ, smul_eq_mul, Fintype.card_fin]
  ring

/-- **Exact event cardinality.** For disjoint `A`, `B`, the number of order enumerations
separating `(A, B)`, times `C(|A|+|B|, |A|)`, equals `(card α)!`. -/
theorem card_separationEvent_mul_choose (A B : Finset α) (hdisj : Disjoint A B) :
    (separationEvent A B).card * (A.card + B.card).choose A.card
      = Nat.factorial (Fintype.card α) := by
  set n := Fintype.card α with hn
  set a := A.card with ha
  set b := B.card with hb
  have hk : a + b ≤ n := by
    have hcardS : (A ∪ B).card = a + b := by rw [Finset.card_union_of_disjoint hdisj]
    have : (A ∪ B).card ≤ n := by
      rw [hn, ← Finset.card_univ]; exact Finset.card_le_univ _
    omega
  rw [card_separationEvent_eq A B hdisj]
  have h1 : (a + b).choose a * a.factorial * b.factorial = (a + b).factorial := by
    have := Nat.choose_mul_factorial_mul_factorial (Nat.le_add_right a b)
    simpa [Nat.add_sub_cancel_left] using this
  have h2 : n.choose (a + b) * (a + b).factorial * (n - (a + b)).factorial = n.factorial :=
    Nat.choose_mul_factorial_mul_factorial hk
  calc n.choose (a + b) * a.factorial * b.factorial * (n - (a + b)).factorial * (a + b).choose a
      = n.choose (a + b) * ((a + b).choose a * a.factorial * b.factorial)
          * (n - (a + b)).factorial := by ring
    _ = n.choose (a + b) * (a + b).factorial * (n - (a + b)).factorial := by rw [h1]
    _ = n.factorial := h2

/-- **Pairwise disjointness.** If `A i ∩ B i = ∅`, `A i ∩ B j ≠ ∅` and `A j ∩ B i ≠ ∅`,
then no order enumeration can separate both `(A i, B i)` and `(A j, B j)`. -/
theorem separationEvents_disjoint {Ai Bi Aj Bj : Finset α}
    (hcross_ij : (Ai ∩ Bj).Nonempty) (hcross_ji : (Aj ∩ Bi).Nonempty) :
    Disjoint (separationEvent Ai Bi) (separationEvent Aj Bj) := by
  rw [Finset.disjoint_left]
  intro e heBi heBj
  rw [mem_separationEvent] at heBi heBj
  rcases hcross_ij with ⟨x, hx⟩
  rcases hcross_ji with ⟨y, hy⟩
  simp only [Finset.mem_inter] at hx hy
  have h1 : e x < e y := heBi hx.1 hy.2
  have h2 : e y < e x := heBj hy.1 hx.2
  exact lt_asymm h1 h2

end SetPairs
