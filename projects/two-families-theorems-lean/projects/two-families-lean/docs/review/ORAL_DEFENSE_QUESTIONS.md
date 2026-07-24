# Oral Defense Questions

Twenty-nine challenging questions about the development. **Attempt them unaided first;**
answers follow in a separate section below.

## Questions

### Permutation counting
1. Why are the separation events for distinct indices pairwise disjoint?
2. Why is the separation-event cardinality independent of elements outside `A∪B`?
3. Why does the count `C(n,a+b)·a!·b!·(n−a−b)!` factor exactly the way it does?
4. Where, precisely, is cross-intersection in *both* directions used?
5. Why avoid a probability argument, and what would it have cost formally?
6. How is a "total order" represented, and why an `Equiv` rather than a `LinearOrder`
   instance?
7. Why is `separationEvent` marked `noncomputable`, and does that weaken anything?
8. How does the proof avoid natural-number division in the final identity?

### Triangular independence
9. Why select the *maximal* nonzero-coefficient index (not the minimal)?
10. What breaks if `K` is only a commutative ring, not a field?
11. How does the lower-triangular dual differ, and why is the extremum flipped?
12. Where is `hdiag` (diagonal nonvanishing) actually used in the contradiction?

### Exterior algebra
13. Why does exterior multiplication vanish off the diagonal (`i<j`)?
14. Why is the diagonal decomposable nonzero when `Uᵢ∩Wᵢ=0`?
15. Why is `dim ⋀^a V = C(a+b,a)`?
16. How does `ιMulti_mul_ιMulti` relate a product of decomposables to a single one?
17. What is the role of `Fin.append` and `finSumFinEquiv` in the concatenation lemma?
18. Which direction (vanishing vs. nonvanishing) is already in Mathlib, and which did
    you add?

### Moment curve / bridge
19. Why are moment-curve vectors nonzero?
20. Why does trivial span intersection follow from independence of the *union* family?
21. Why does the proof work when `|s| < d` (fewer vectors than the dimension)?
22. Where is injectivity of the label `t` used?
23. How is an injective `α ↪ ℚ` obtained for an arbitrary finite `α`?
24. Why can the ground set be larger than `a+b`?

### Skew orientation and edge cases
25. Where is the skew orientation `i<j` used, and how does it match the triangular
    lemma?
26. How are the edge cases `a=0`, `b=0`, `m=0` handled in the subspace theorem?
27. How is the `d=0` corner discharged in `frankl_kalai_skew`?

### Meta
28. Which parts rely on classical choice, and could any be made constructive?
29. Which lemmas are genuinely absent from Mathlib, and which are thin wrappers?

---

## Answers

1. If `x∈Aᵢ∩Bⱼ` and `y∈Aⱼ∩Bᵢ`, an order separating `(Aᵢ,Bᵢ)` forces `e x<e y` and one
   separating `(Aⱼ,Bⱼ)` forces `e y<e x`; both cannot hold (`separationEvents_disjoint`).
2. Elements outside `A∪B` contribute only the free factor `(n−a−b)!` (the relative
   order of the complement), which cancels against `C(n,a+b)` in the identity; they
   never constrain `Separates` (`fiber_card_eq`, `card_separationEvent_eq`).
3. `C(n,a+b)` chooses the positions of `A∪B`; `a!·b!` orders `A` then `B` inside those
   positions; `(n−a−b)!` orders the rest. These three choices are independent, which is
   exactly the ordering-factorization equivalence.
4. In `separationEvents_pairwiseDisjoint`, which calls `separationEvents_disjoint` with
   both `hcross hij` and `hcross hij.symm`.
5. A probability phrasing needs `ℝ`-valued measures and division; formally heavier and
   it obscures the fibre structure. The integer count is also exactly what the
   regression tests check.
6. As `α ≃ Fin n`; an `Equiv` gives a ranking with a computable inverse and directly
   supports `Fintype.card_equiv` counting, avoiding order-instance bookkeeping.
7. It filters over all equivalences, which are not computably enumerable without
   `Classical`; `noncomputable` is a compile-time annotation only — the `Finset` and
   its `card` are still perfectly well-defined mathematically.
8. Via `Nat.choose_mul_factorial_mul_factorial` twice: `C(a+b,a)a!b!=(a+b)!` and
   `C(n,a+b)(a+b)!(n−a−b)!=n!`; multiplying the count by `C(a+b,a)` yields `n!` with no
   division.
9. Because the hypothesis annihilates `Tⱼ(uᵢ)` for `i<j`; at the *largest* active index
   all smaller-index terms die by the hypothesis and all larger-index terms die by
   maximality.
10. The final step `smul_eq_zero` needs `gⱼ≠0 ⟹ Tⱼ(uⱼ)=0`, i.e. no zero divisors /
    invertibility — a field (or at least a domain) is required.
11. It uses `S.min'` and the hypothesis `j<i ⟹ Tⱼ(uᵢ)=0`; the minimal active index
    makes larger-index terms vanish by the hypothesis and smaller ones by minimality.
12. `gⱼ•Tⱼ(uⱼ)=0` with `gⱼ≠0` forces `Tⱼ(uⱼ)=0`, contradicting `hdiag j`.
13. `Uᵢ∩Wⱼ≠0` makes the concatenated bases linearly dependent, so their decomposable
    wedge is `0` (`AlternatingMap.map_linearDependent`).
14. `Uᵢ∩Wᵢ=0` plus `dim Uᵢ+dim Wᵢ=dim V` makes the union a basis; independent families
    have nonzero decomposable wedge (`ιMulti_ne_zero_of_linearIndependent`).
15. `exteriorPower.finrank_eq K a` gives `C(dim V,a)`, and `dim V=a+b`.
16. `ιMulti a u * ιMulti b w = ιMulti (a+b) (Fin.append u w)`: the product of two
    decomposables is the decomposable of the concatenated family.
17. `finSumFinEquiv` identifies `Fin a ⊕ Fin b ≃ Fin (a+b)`, and `Fin.append` is the
    concatenation; `sumElim_comp_finSumFinEquiv_symm` bridges `Sum.elim` (used by
    `LinearIndependent.sum_type`) and `Fin.append`.
18. Vanishing (`map_linearDependent`) is in Mathlib; the nonvanishing directions
    (`ιMulti_ne_zero_*`) and concatenation (`ιMulti_mul_ιMulti`) were added here.
19. Their zeroth coordinate is `t x^0 = 1 ≠ 0` (`momentCurve_ne_zero`, needs `d≠0`).
20. `LinearIndependent.disjoint_span_image` on the independent union family gives the
    two sub-spans disjoint; disjoint spans meet in `⊥`.
21. The interpolation polynomial `∏_{k≠i}(X−t_k)` has degree `|s|−1 < d` regardless of
    whether `|s|=d`; only the relations for `r<d` are used, so no square matrix is
    assumed.
22. In showing `p(tᵢ)≠0`: `∏_{k≠i}(tᵢ−t_k)≠0` needs `tᵢ≠t_k`, i.e. injectivity.
23. Compose `Fintype.equivFin α : α ≃ Fin (card α)` with the injection `Fin _ ↪ ℕ ↪ ℚ`.
24. Only the ambient dimension `d=a+b` is fixed; `α` is an arbitrary finite type,
    embedded into ℚ, so `|α|` may exceed `a+b`.
25. In `lovasz_frankl_subspaces`, `hcross hij` (`i<j`) feeds
    `append_wedge_eq_zero (Uᵢ)(Wⱼ)`, giving `Tⱼ(uᵢ)=0` for `i<j` — exactly the
    upper-triangular hypothesis; `frankl_kalai_skew` passes its own `i<j` through.
26. No special handling: empty bases and `ιMulti K 0 = 1` are absorbed by the general
    argument; `a=0`⟹`Uᵢ=⊥` with `uᵢ=1≠0`, `m=0`⟹`0≤C(a+b,a)` trivially.
27. `by_cases d=0`: then `a=0`, so `Aᵢ=∅`, contradicting the nonempty `Aᵢ∩Bⱼ` from
    `hcross`; the branch is closed by `exfalso`.
28. `Classical.choice` underlies the noncomputable `separationEvent` filtering, basis
    selection (`finBasisOfFinrankEq`), and various `Fintype`/`Equiv` constructions. The
    core algebra could in principle be made more constructive, but the development
    embraces classical Mathlib conventions; making it constructive is not attempted.
29. Genuinely absent: `of_upperTriangular_maps`(+dual), `ιMulti_ne_zero_*`,
    `ιMulti_mul_ιMulti`, the separation-event count chain, moment-curve independence and
    span-intersection lemmas. Thin wrappers (keep out of Mathlib):
    `card_orderEnumerations`, `ιMulti_eq_zero_of_linearDependent`.
