# Mock Reviews

Three independent simulated reviews of the paper and artifact. They are deliberately
critical and not uniformly positive. Scores use a standard 1–5 scale (1 reject, 5
strong accept) with a separate confidence (1–4).

---

## Reviewer 1 — Lean / Mathlib expert

**Summary.** A modular Lean 4 / Mathlib formalization of the Bollobás–Lovász–Frankl
two-families theorems along two proof routes. The infrastructure (triangular
independence, exterior nonvanishing/concatenation, moment-curve general position,
separation-event counting) is the most valuable part and is largely Mathlib-shaped.

**Strengths.**
* Clean module DAG with two genuinely independent routes; no circular imports.
* Generic lemmas (`of_upperTriangular_maps`, `ιMulti_ne_zero_*`, `ιMulti_mul_ιMulti`,
  `momentCurve_linearIndependent`) are stated without application-specific baggage.
* Axiom hygiene is exemplary: only the three standard axioms, no `sorry`/`unsafe`.
* A concrete, dependency-ordered Mathlib PR plan is included.

**Weaknesses.**
* Every file uses blanket `import Mathlib`; unacceptable for upstream, and it inflates
  build time. Minimal imports are only *estimated*, not produced.
* `autoImplicit` is left at the default `true`, contrary to Mathlib convention.
* The moment-curve layer is fixed to `ℚ`; the natural upstream statement is over an
  arbitrary field. This limits immediate reuse.
* One nonterminal `simp` in `uniform_bollobas_sharp`.
* `card_orderEnumerations` and `ιMulti_eq_zero_of_linearDependent` are thin wrappers;
  should not be upstreamed as-is.

**Detailed questions.**
1. Can `of_upperTriangular_maps` be generalized to an arbitrary `LinearOrder` `Fintype`
   index and to a division ring?
2. Why interpolation rather than `Matrix.det_vandermonde` for the square case — is the
   determinant route actually harder in Lean, or just different?
3. What is the build time contribution of `import Mathlib` vs. minimal imports?

**Confidence:** 4. **Score:** 3 (borderline accept as a formalization contribution;
requires the import/generality cleanup before Mathlib submission).

**Changes required for acceptance.** Produce minimal imports for at least the PR-1..3
declarations; generalize moment curve to a field; set `autoImplicit false`; remove the
nonterminal `simp`.

---

## Reviewer 2 — Extremal combinatorics expert

**Summary.** The paper formalizes the correct theorems (weighted Bollobás, uniform
corollary + sharpness, Lovász–Frankl subspace, Frankl–Kalai skew) with faithful
statements and correct hypotheses, including the delicate skew direction `i<j`.

**Strengths.**
* Statements are mathematically faithful: `⊓ = ⊥` (not `≠ ⊤`), `Disjoint` = empty
  intersection, skew `i<j` correctly weaker than symmetric `i≠j`.
* The exact separation-event count `C(n,a+b)a!b!(n−a−b)!` is the right object and is
  proved without probability or division.
* Sharpness of the uniform bound is included, and the adversarial tests convincingly
  show every hypothesis is needed (notably that the weighted inequality genuinely needs
  *both* cross directions and the skew theorem needs uniformity).

**Weaknesses.**
* No equality/extremal *classification* — only the single complement family. For a
  combinatorics audience this is the natural next question and its absence should be
  stated even more prominently.
* Historical attribution of the skew theorem is compressed; the Frankl (1982) vs.
  Kalai (1984) contributions and Lovász's priority deserve a sentence each.
* The paper claims no new mathematics (correct), but could better articulate *why*
  formalizing the two routes together is scientifically interesting beyond "it was
  done."

**Detailed questions.**
1. Does the formalization say anything about the equality cases, even partially?
2. Is the subspace theorem's field-generality exploited, or is only `ℚ` ever used
   downstream?
3. Could the weighted inequality's sharpness (equality iff complement family) be
   formalized with modest effort?

**Confidence:** 3. **Score:** 3 (accept as a faithful formalization; the lack of
equality classification caps the mathematical novelty, but none is claimed).

**Changes required for acceptance.** Sharpen the limitations paragraph on equality
cases; expand historical attribution; state explicitly that field-generality of the
subspace theorem is a genuine (if unused-downstream) strengthening.

---

## Reviewer 3 — Formalization-paper reviewer

**Summary.** A well-scoped formalization paper with a clear thesis (two proofs, one
triangular certificate), honest claims, and strong reproducibility materials.

**Strengths.**
* The central thesis is genuinely supported by the code (the algebraic route literally
  calls a triangular-independence lemma; the counting route uses disjoint exactly-sized
  events).
* Reproducibility is taken seriously: pinned toolchain, forbidden-token scan,
  exact-arithmetic regression tests, artifact stress test, duplicate-build check.
* AI use is disclosed factually, with a clear separation between kernel-checking and
  semantic fidelity.
* Cautious novelty wording; no "first formalization" overclaim.

**Weaknesses.**
* The novelty audit's external-library rows rely on prior knowledge rather than live
  search (disclosed, but a genuine gap).
* The paper is at the low end of the target length (8 pages); Sections 7–8 could carry
  one more concrete Lean excerpt each.
* The dependency figure is ASCII art rather than a generated vector graphic.
* Some evaluation numbers (build time) are environment-specific; should be labelled as
  such (they are, but prominently).

**Detailed questions.**
1. Can the external novelty search be re-run against live indexes before camera-ready?
2. Is the 133 s build time with a warm Mathlib cache or cold?
3. Would a human co-author sign off on the `SeparationEvents.lean` proof after reading
   `docs/review/HUMAN_REVIEW_GUIDE.md`?

**Confidence:** 4. **Score:** 4 (accept; a solid, honest formalization paper with
reusable output).

**Changes required for acceptance.** Re-run live novelty search; label build-time
provenance; optionally upgrade the dependency figure.

---

## Aggregate

| Reviewer | Score | Confidence |
|----------|-------|-----------|
| R1 (Lean/Mathlib) | 3 | 4 |
| R2 (combinatorics) | 3 | 3 |
| R3 (formalization) | 4 | 4 |

**Overall:** weak-to-clear accept as a *formalization* contribution, conditional on the
import/generality cleanup (R1), sharper limitations + attribution (R2), and a live
novelty re-check (R3). No reviewer disputes the correctness or faithfulness of the
machine-checked results. Responses in `docs/review/REVISION_RESPONSE.md`.
