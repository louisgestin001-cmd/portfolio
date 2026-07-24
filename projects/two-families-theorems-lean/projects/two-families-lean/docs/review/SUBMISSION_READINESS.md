# Submission Readiness

Four independent verdicts, each with its evidence. The global verdict is `PASS` only if
all four pass. Assessed against the actual compiled/measured state of the repository
(see `docs/review/PRE_REVISION_SNAPSHOT.md`), not a prior report.

---

## A. Mathematical kernel correctness — **PASS**

* All seven principal declarations compile (`lake build` → success, 8039 jobs, ≈133 s
  warm-cache).
* Zero project-local `sorry`, `admit`, custom `axiom`, `unsafe`, or `@[implemented_by]`
  (`scripts/check_forbidden.sh` exit 0; `rg` confirms the only `sorry` substring is the
  word `sorryAx` in a docstring; `scripts/statistics.py` reports `lines with sorry: 0`).
* Every principal theorem's `#print axioms` lists exactly
  `[propext, Classical.choice, Quot.sound]`.

## B. Semantic fidelity — **PASS**

* `docs/proofs/PRINCIPAL_THEOREMS.md`: each public statement given with English reading, edge
  cases, non-vacuity witness, and a fidelity verdict (exactly-equivalent, or a genuine
  strengthening — never weaker).
* `docs/proofs/INDEPENDENT_PROOF_AUDIT.md`: every principal theorem's informal proof reconstructed
  from the Lean definitions; **no unresolved mismatch** on any of the specific points
  (event count, disjointness, triangular orientation, exterior dimension, rectangular
  moment curve, ground-set-larger-than-`a+b`, `d=0` corner).
* `docs/proofs/ADVERSARIAL_TESTS.md` + `scripts/adversarial_checks.py`: each principal hypothesis
  shown load-bearing by an exact counterexample (`OVERALL: PASS`).
* Non-vacuity: witnessed by `uniform_bollobas_sharp` (bound attained) and the
  moment-curve instances; no theorem is vacuous.

## C. Artifact reproducibility — **PASS** (with documented Mathlib-fetch caveat)

* Fresh extraction of `two_families_lean_artifact.zip` into a clean directory
  reproduces, **identically**: forbidden scan (exit 0), `verify_small_cases.py`
  (`PASS`), `adversarial_checks.py` (`PASS`), `statistics.py` (`51` decls, `0` sorry),
  and the 8-page PDF (`docs/review/ARTIFACT_STRESS_TEST.md`).
* Extracted sources are **byte-identical** to the in-place sources
  (`diff -rq`, `md5sum`), and the toolchain/Mathlib pins are fixed, so the Lean build
  outcome is deterministic.
* No user-specific paths, credentials, `.lake` outputs, or private metadata in the
  archive.
* **Caveat (not a defect):** a from-scratch `lake build` from a bare extraction first
  fetches and compiles Mathlib `v4.28.0` (network + long compile), standard for any
  Mathlib project; this was verified in-place (warm cache) rather than re-run offline
  from the extraction. An evaluator with network reproduces it via
  `lake exe cache get && lake build`.

## D. Paper readiness — **PASS**

* `paper/main.pdf` compiles (tectonic) to **8 pages** of main text (within the
  approximate 8–10 target; at the lower bound), plus references.
* Citations verified for internal consistency and entry type
  (`docs/research/BIBLIOGRAPHY_AUDIT.md`); the previous missing-`\cite` bug is fixed (0 undefined
  references in the compiled PDF). DOIs deferred (no live access; none fabricated).
* All paper claims correspond to code (Tables A/B, the measured evaluation, the axiom
  statement); novelty wording is cautious (`docs/research/NOVELTY_AUDIT.md`); no "first
  formalization" overclaim.
* Mock-review objections addressed (`docs/review/REVISION_RESPONSE.md`); AI use disclosed
  (`AI_USE_STATEMENT.md`, paper §10); no nonexistent file is reported as present.

---

## Global verdict — **PASS**

All four sections pass. Two honestly-flagged, non-blocking caveats remain: (i) a
from-scratch Lean build requires the standard Mathlib fetch (verified in-place with
byte-identical sources); (ii) the external-library novelty search could not be run
against live indexes and should be re-confirmed before camera-ready. Neither affects the
correctness, faithfulness, or reproducibility of the machine-checked results.

## Mandatory-item checklist (1–18 from the original spec)

| # | Item | Status |
|---|------|--------|
| 1 | Weighted Bollobás (`weighted_bollobas`) | PASS |
| 2 | Exact permutation event count (`card_separationEvent_mul_choose`) | PASS |
| 3 | Uniform corollary (`uniform_bollobas`) | PASS |
| 4 | Sharpness (`uniform_bollobas_sharp`) | PASS |
| 5 | Triangular independence (`of_upperTriangular_maps`) | PASS |
| 6 | Exterior vanishing/nonvanishing + multiplication | PASS |
| 7 | Lovász–Frankl subspaces (`lovasz_frankl_subspaces`) | PASS |
| 8 | Moment-curve GP (`momentCurve_linearIndependent`) | PASS |
| 9 | Frankl–Kalai skew (`frankl_kalai_skew`) | PASS |
| 10 | Exact small-case script | PASS |
| 11 | Clean build | PASS |
| 12 | No `sorry`/`admit`/custom axiom/unsafe | PASS |
| 13 | Theorem map (`THEOREM_MAP.md`) | PASS |
| 14 | Semantic audit (`docs/proofs/SEMANTIC_AUDIT.md`, `docs/proofs/INDEPENDENT_PROOF_AUDIT.md`) | PASS |
| 15 | Related-formalization / novelty audit (`docs/research/NOVELTY_AUDIT.md`) | PASS (live re-check pending) |
| 16 | Mathlib extraction plan (`docs/upstream/MATHLIB_EXTRACTION.md`, `docs/upstream/MATHLIB_PR_PLAN.md`) | PASS |
| 17 | Anonymous paper source + PDF | PASS (8 pages) |
| 18 | PDF claims match Lean | PASS |
