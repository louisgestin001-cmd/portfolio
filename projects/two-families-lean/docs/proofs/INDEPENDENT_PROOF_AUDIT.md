# Independent Proof Audit

For each principal theorem, an informal proof is reconstructed **from the actual Lean
definitions** (not from the previous report), and the specific correctness points
demanded by the task are checked against the source.

Ground-truth definitions used below (from the source):

* `OrderEnumeration α := α ≃ Fin (Fintype.card α)` (`PermutationOrders.lean`).
* `Separates e A B := ∀ ⦃x⦄, x ∈ A → ∀ ⦃y⦄, y ∈ B → e x < e y` (`SeparationEvents.lean`).
* `separationEvent A B := univ.filter (fun e => Separates e A B)`.
* `momentCurve d t x := fun r : Fin d => t x ^ (r:ℕ)` (`MomentCurve.lean`).
* `spanMomentCurve d t S := span ℚ (Set.range (fun x : S => momentCurve d t x))`.

---

## 3.1 Weighted Bollobás

**Goal.** `∑ᵢ 1 / C(|Aᵢ|+|Bᵢ|, |Aᵢ|) ≤ 1`.

**Reconstruction.** Write `n = |α|`. For each `i` the reciprocal equals `|Eᵢ|/n!`
where `Eᵢ = separationEvent (Aᵢ) (Bᵢ)`, because
`|Eᵢ|·C(|Aᵢ|+|Bᵢ|,|Aᵢ|) = n!` (`card_separationEvent_mul_choose`). The `Eᵢ` are
pairwise disjoint (below), so `∑ᵢ |Eᵢ| = |⋃ᵢ Eᵢ| ≤ |OrderEnumeration α| = n!`
(`card_orderEnumerations`). Dividing by `n! > 0` gives the bound. This matches the
Lean proof line by line (`hterm`, `hdisj`, `hbu`, `hle`, final `calc`).

**Point checks.**

* *`Separates` really means "every `A`-element before every `B`-element".* Yes — the
  definition quantifies `x ∈ A`, `y ∈ B` and asserts `e x < e y`. ✔
* *Event count `= C(n,a+b)·a!·b!·(n-a-b)!`.* This is `card_separationEvent_eq`,
  proved by fibring `separationEvent` over the position set `P = e(A∪B)` via
  `Finset.card_eq_sum_card_fiberwise`: each fibre has `a!·b!·(n-a-b)!` elements
  (`fiber_card_eq` × `card_separates_toP`), and there are `C(n,a+b)` position sets.
  Independently correct: choosing where `S=A∪B` lands (`C(n,a+b)`), ordering `A`
  before `B` inside those positions (`a!·b!`), and ordering the complement freely
  (`(n-a-b)!`). ✔
* *Multiplying by `C(a+b,a)` gives `n!`.* From `C(a+b,a)·a!·b! = (a+b)!` and
  `C(n,a+b)·(a+b)!·(n-a-b)! = n!` (`Nat.choose_mul_factorial_mul_factorial`, applied
  twice). No natural-number division is used. ✔
* *Distinct-index events disjoint.* `separationEvents_disjoint`: pick
  `x ∈ Aᵢ∩Bⱼ`, `y ∈ Aⱼ∩Bᵢ`; if `e` separated both pairs then `e x < e y` (from
  `(Aᵢ,Bᵢ)`) and `e y < e x` (from `(Aⱼ,Bⱼ)`), contradiction via `lt_asymm`. This
  needs cross-intersection in **both** directions `i≠j` and `j≠i`, supplied by
  `separationEvents_pairwiseDisjoint` calling `hcross hij` and `hcross hij.symm`. ✔
* *No hidden `Aᵢ∪Bᵢ = univ` assumption.* Confirmed: `card_separationEvent_eq` holds
  for arbitrary disjoint `A, B` in any finite `α`; the complement factor
  `(n-a-b)!` explicitly counts elements outside `A∪B`. The full-support lemma
  `card_separates_full` is only an internal stepping stone. ✔
* *Empty `Aᵢ`/`Bᵢ`.* `C(a+b,a) ≥ 1` and the count identity degenerates correctly
  (`Examples.lean` checks `evCount 3 0 0 · C(0,0) = 3!`). ✔

**Verdict: no mismatch.**

---

## 3.2 Triangular independence

**Goal.** `hdiag : T j (u j) ≠ 0`, `hzero : i < j → T j (u i) = 0` ⟹ `u` independent.

**Reconstruction.** Suppose `∑ᵢ gᵢ • uᵢ = 0` with some `g ≠ 0`. Let
`S = {i : gᵢ ≠ 0}` (nonempty) and `j = S.max'`. Apply the linear map `T j`:
`∑ᵢ gᵢ • T j (uᵢ) = 0`. For `i < j`, `T j (uᵢ) = 0` by `hzero`. For `i > j`,
`i ∉ S` (as `j` is the max of `S`), so `gᵢ = 0`. Only `i = j` survives:
`gⱼ • T j (u j) = 0`. Since `gⱼ ≠ 0` and `K` is a field, `T j (u j) = 0`,
contradicting `hdiag`.

**Orientation check (the crux the task asks for).** The Lean proof selects
`j = S.max'` (the **maximal** nonzero coefficient) and `hzero` annihilates
`T j (u i)` for `i < j`. These are consistent: at the largest active index `j`, all
*smaller* active indices `i < j` are annihilated by `hzero`, and all *larger* indices
are inactive by maximality. If instead one had `hzero` for `j < i` (lower-triangular),
one must pick the **minimal** index — which is exactly what
`of_lowerTriangular_maps` does (`S.min'`, `hzero : j < i → …`). Both orientations are
present and each pairs its extremum correctly. ✔

**Where used.** `lovasz_frankl_subspaces` uses the **upper** version with the skew
hypothesis `i < j → Uᵢ ⊓ Wⱼ ≠ ⊥`, giving `T j (u i) = 0` for `i < j`. ✔

**Verdict: no mismatch; orientation is correct.**

---

## 3.3 Subspace theorem

**Goal.** `m ≤ C(a+b, a)`.

**Reconstruction.** Choose bases `bU i` of `Uᵢ` (`Module.finBasisOfFinrankEq`, valid
since `dim Uᵢ = a`), similarly `bW i`. Set `uᵢ = ιMulti K a (bU i ↪ V) ∈ ⋀^a V` and
`wⱼ = ιMulti K b (bW j ↪ V) ∈ ExteriorAlgebra K V`. Define
`T j = (· * wⱼ) ∘ (⋀^a V).subtype`. Then
`T j (u i) = ιMulti K (a+b) (append (bU i) (bW j))` (via
`ExteriorAlgebra.ιMulti_mul_ιMulti` and `exteriorPower.ιMulti_apply_coe`).

* Diagonal: `Uᵢ ⊓ Wᵢ = ⊥` ⟹ the appended bases are independent (spans meet only in
  `0`) ⟹ decomposable `≠ 0` (`append_wedge_ne_zero`). So `T i (u i) ≠ 0`.
* Off-diagonal `i < j`: `Uᵢ ⊓ Wⱼ ≠ ⊥` ⟹ appended bases are **dependent** ⟹
  decomposable `= 0` (`append_wedge_eq_zero`). So `T j (u i) = 0`.

Triangular independence gives `u` independent in `⋀^a V`, so
`m ≤ dim ⋀^a V = C(a+b, a)` (`exteriorPower.finrank_eq K a` with `dim V = a+b`).

**Point checks.**

* *Decomposable of `Uᵢ` nonzero.* `append_wedge_ne_zero` calls
  `ιMulti_ne_zero_of_linearIndependent` on the independent appended bases; specialising
  to `b = 0` (empty `W`) shows `uᵢ ≠ 0` too. ✔
* *Diagonal nonvanishing.* Uses `hdiag i : Uᵢ ⊓ Wᵢ = ⊥` → `disjoint_iff` → span
  disjointness → independence of `append` → nonvanishing. ✔
* *Nontrivial `Uᵢ ⊓ Wⱼ` forces dependence.* `not_linearIndependent_append_of_inf_ne_bot`:
  if the appended family were independent, `Sum.elim` would be independent, forcing
  the spans disjoint (`linearIndependent_sum`), contradicting `⊓ ≠ ⊥`. ✔
* *Dependence forces vanishing.* `ιMulti_eq_zero_of_linearDependent =
  AlternatingMap.map_linearDependent`. ✔
* *Correct index direction.* `hcross hij` with `i < j` feeds
  `append_wedge_eq_zero (U i) (W j)` producing `T j (u i) = 0` — matches the
  upper-triangular hypothesis. ✔
* *Ambient dimension `= C(a+b,a)`.* `exteriorPower.finrank_eq K a` gives
  `dim ⋀^a V = C(dim V, a) = C(a+b, a)` after `hdimV`. ✔

**Verdict: no mismatch.**

---

## 3.4 Moment curve

**Goal.** At most `d` distinct vectors `(1, t, …, t^{d-1})` are independent.

**Reconstruction.** A vanishing combination `∑_{j∈s} u_j · v_j = 0` gives, coordinate
by coordinate, `∑_j u_j t_j^r = 0` for all `r < d` (`hcoords`). Hence for every
polynomial `p` of degree `< d`, `∑_j u_j p(t_j) = 0` (`hpoly`, by expanding `p` in the
monomial basis). Fix `i ∈ s` and take `p = ∏_{j≠i}(X - t_j)`; its degree is
`|s|-1 < d` (`hp_deg`). Then `p(t_j) = 0` for `j ≠ i` (`hp_eval_ne`) and
`p(t_i) ≠ 0` (`hp_eval_i`, using injectivity of `t`). So `∑_j u_j p(t_j) = u_i p(t_i)`
and `u_i p(t_i) = 0`, giving `u_i = 0`. As `i` was arbitrary, `u ≡ 0`.

**Point checks.**

* *`|s| < d` case.* `hp_deg` proves `p.natDegree = |s|-1 < |s| ≤ d`. The proof uses
  only the relations for `r < d`, never that a coordinate `r = |s|` exists or that the
  matrix is square. No `|s| = d` requirement is smuggled in. ✔
* *No square-matrix reduction assumed.* The argument is purely interpolation; the
  rectangular `|s| × d` case is handled directly, which is exactly the requested
  behaviour ("do not assume the rectangular Vandermonde matrix has independent rows
  without deriving it"). ✔
* *Injectivity used.* `hp_eval_i` invokes `ht.ne`. If `t` were non-injective, two
  equal labels would make `p(t_i) = 0` and the argument would (correctly) fail. ✔

**Verdict: no mismatch.**

---

## 3.5 Set-to-subspace bridge

**Goal (via `frankl_kalai_skew`).** Turn set pairs into subspaces and apply Thm 5.

**Reconstruction.** `t x = (Fintype.equivFin α x : ℕ) : ℚ` is injective (composite of
the `Fin`-equiv and the injective `ℕ ↪ ℚ`). Set `d = a+b`, `Uᵢ = spanMomentCurve d t
(Aᵢ)`, `Wᵢ = spanMomentCurve d t (Bᵢ)`. Then:

* `dim (Fin d → ℚ) = d = a+b` (`Module.finrank_fin_fun`). ✔
* `dim Uᵢ = |Aᵢ| = a` because `|Aᵢ| = a ≤ d` (`finrank_spanMomentCurve`, which uses
  `finrank_span_eq_card` on the independent moment vectors). ✔
* `Uᵢ ⊓ Wᵢ = ⊥`: `Aᵢ, Bᵢ` disjoint and `|Aᵢ|+|Bᵢ| = a+b = d ≤ d`
  (`inf_spanMomentCurve_eq_bot`, via `LinearIndependent.disjoint_span_image` on the
  independent union family). ✔
* For `i < j`, `Uᵢ ⊓ Wⱼ ≠ ⊥`: `Aᵢ ∩ Bⱼ ≠ ∅` gives a common `x`; `momentCurve d t x`
  is nonzero (zeroth coordinate `= 1`, `momentCurve_ne_zero`, needs `d ≠ 0`) and lies
  in both spans (`inf_spanMomentCurve_ne_bot`). ✔

**Point checks.**

* *Disjoint sets of total size `≤ a+b` → trivial intersection.* `inf_spanMomentCurve_eq_bot`
  hypothesis is `|S|+|T| ≤ d`; here equality `= d`. ✔
* *Intersecting sets → nonzero common vector.* Yes, the common `momentCurve` vector.
  ✔
* *Common vector nonzero.* `momentCurve_ne_zero` uses coordinate `0` value `1`. ✔
* *Ground set may exceed `a+b`.* `α` arbitrary; only `d = a+b` bounds dimension. The
  `frankl_kalai_skew` proof never assumes `|α| = a+b`. ✔
* *Injective rational labels exist for any finite `α`.* `Fintype.equivFin` composed
  with `ℕ ↪ ℚ`; proven inline (`ht`). ✔
* *`d = 0` corner.* Handled by `by_cases hd0 : d = 0`: then `a = 0`, `Aᵢ = ∅`,
  contradicting `hcross hij`'s nonempty intersection — so this branch is discharged by
  `exfalso`. (For `m ≤ 1` no `i < j` exists, so `hcross` is vacuous and the branch is
  genuinely unreachable when `m ≥ 2`; the code closes it correctly.) ✔

**Verdict: no mismatch.**

---

## Overall verdict

All five audited chains reconstruct to the intended informal proofs, and every
specific correctness point requested in §3 of the task is satisfied by the actual
Lean source. **No semantic mismatch was found; no formal statement required
correction.**
