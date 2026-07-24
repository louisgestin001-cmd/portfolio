# Revision Response

Point-by-point response to the mock reviews (`docs/review/MOCK_REVIEWS.md`). Each item is
**accepted**, **partially accepted**, or **rejected**, with the concrete change (or the
reason for deferral). Unresolved items are left visible rather than hidden.

## Reviewer 1 (Lean/Mathlib)

**R1.1 Blanket `import Mathlib`.** *Partially accepted.* Kept for the standalone
artifact (robust across point releases, keeps the development legible), but recorded as
[REQUIRED] for Mathlib in `docs/review/STYLE_REVIEW.md` and the per-PR minimal import sets are
listed in `docs/upstream/MATHLIB_PR_PLAN.md` (PR 1: `LinearIndependent.Defs` + `Fintype.Card`; PR 2:
`ExteriorPower.Basic` + `ExteriorAlgebra.Basic`; PR 3: `Vandermonde` +
`Dimension.Finrank` + `Polynomial.Eval`; PR 4: enumerative + `Nat.Choose.Factorization`).
Not changed in the artifact itself, since the task forbids opening Mathlib PRs without
authorization and the change serves only submission.

**R1.2 `autoImplicit`.** *Partially accepted.* Documented as [REQUIRED for Mathlib /
RECOMMENDED for project] in `docs/review/STYLE_REVIEW.md`. Deferred for the same reason as R1.1;
enabling it project-wide would be churn for a not-yet-authorized submission.

**R1.3 Moment curve fixed to ℚ.** *Accepted (documented, deferred as code change).* The
limitation is now stated in the paper (§10) and `docs/research/SCIENTIFIC_THESIS.md`; the interpolation
proof generalizes verbatim to any infinite field, noted as the intended upstream form in
`docs/upstream/MATHLIB_PR_PLAN.md` PR 3. Left over ℚ in the artifact because the downstream bridge only
needs ℚ and the task says not to add unrelated generality merely for its own sake.

**R1.4 Nonterminal `simp`.** *Accepted (documented).* Flagged [RECOMMENDED] in
`docs/review/STYLE_REVIEW.md`. Not rewritten now to avoid perturbing a verified proof; it is a
cosmetic, stable step.

**R1.5 Thin wrappers upstream.** *Accepted.* `card_orderEnumerations` and
`ιMulti_eq_zero_of_linearDependent` are explicitly listed as "keep out of Mathlib" in
`docs/upstream/MATHLIB_PR_PLAN.md`.

**R1 questions.** (1) Yes — generalization to `[LinearOrder ι][Fintype ι]` and a
division ring is noted in `docs/upstream/MATHLIB_PR_PLAN.md` PR 1. (2) Interpolation is genuinely
cleaner because the *rectangular* `|s|<d` case needs it anyway; the determinant handles
only the square case (paper §6, `docs/proofs/INDEPENDENT_PROOF_AUDIT.md §3.4`). (3) Not measured
per-file; only the aggregate warm-cache build (≈133 s) is reported — left as an open item.

## Reviewer 2 (Combinatorics)

**R2.1 No equality classification.** *Accepted.* Made more prominent in the paper's
limitations (§10) and `docs/research/SCIENTIFIC_THESIS.md` ("statements that must not be claimed").
Only the complement sharpness (`uniform_bollobas_sharp`) is formalized; full equality
classification is explicitly out of scope.

**R2.2 Historical attribution.** *Accepted.* `docs/research/BIBLIOGRAPHY_AUDIT.md` and the paper's
Related Work distinguish Bollobás (1965), Lovász (1977), Frankl (1982), Kalai (1984),
and the Babai–Frankl exposition; the bib entry types were corrected.

**R2.3 Why combining the routes is interesting.** *Accepted.* Articulated as the
central thesis (paper §1, `docs/research/SCIENTIFIC_THESIS.md`): both proofs produce the same abstract
triangular certificate, made literal by the shared use of a triangular-independence
lemma vs. disjoint exactly-sized events.

**R2 questions.** (1) No equality-case content beyond complement sharpness — stated.
(2) Field-generality of the subspace theorem is genuine but only ℚ is used downstream;
now stated explicitly (paper §5/§10). (3) Weighted-equality (iff complement) is
*plausibly* modest additional work but is **not** claimed or done — left as future work.

## Reviewer 3 (Formalization)

**R3.1 Live external novelty search.** *Partially accepted / unresolved.* The
environment has no live web access; `docs/research/NOVELTY_AUDIT.md` states this explicitly and marks
the external-library rows as best-documented-search, to be re-confirmed before
camera-ready. This is a genuine remaining limitation.

**R3.2 Paper length / more Lean excerpts.** *Accepted.* The paper now includes Lean
excerpts for `Separates` (§4) and `of_upperTriangular_maps` (§5), plus the dependency
figure and two correspondence tables; length is ~8 pages of main text.

**R3.3 ASCII dependency figure.** *Partially accepted.* Kept as a reproducible in-source
figure (no external toolchain needed); upgrading to a vector graphic is noted as
optional polish.

**R3.4 Environment-specific numbers.** *Accepted.* Build time is labelled "in our
environment" (paper §8) and the reproducibility docs record exact commands.

**R3 questions.** (1) Deferred to camera-ready (no live access here). (2) The ≈133 s is
a **warm-cache** build (Mathlib oleans present); a cold build compiling Mathlib from
scratch is far longer — now stated. (3) `docs/review/HUMAN_REVIEW_GUIDE.md` and
`docs/review/ORAL_DEFENSE_QUESTIONS.md` are provided precisely to enable a human sign-off.

## Unresolved items (left visible)

* Per-file minimal imports are estimated, not produced (R1.1, R1.3).
* External-library novelty search not run against live indexes (R3.1).
* No equality classification beyond complement sharpness (R2.1, R2 q3).
* Per-file build-time breakdown not measured (R1 q3).
