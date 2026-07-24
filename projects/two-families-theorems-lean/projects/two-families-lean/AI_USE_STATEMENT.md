# AI Use Statement

This entire project was produced with substantial AI assistance across its full
workflow, not only during the Lean formalization. AI tools, including Aristotle by
Harmonic, contributed to planning, research support, proof development, code, tests,
documentation, translation, auditing, revision, and repository presentation. This
statement records factually what that means for the trust one may place in the artifact.

## What was AI-generated or AI-modified

* AI assistance was used throughout the project: framing the work, exploring proof
  strategies, drafting and refining Lean code, creating tests, organizing files,
  writing explanations, and preparing the repository for publication.
* Substantial portions of the Lean proofs, the paper, the audit documents, the scripts,
  and the repository documentation were AI-generated or AI-modified.
* The French translation was produced with AI assistance and checked for consistency
  with the English report and the Lean theorem names.
* Human direction determined the objectives, requested revisions and verification,
  selected what to retain, and made the final publication decisions.

## What kernel-checking does and does not guarantee

* **Does guarantee:** every Lean proof in the development is accepted by the Lean 4
  kernel *relative to the theorem statement it proves*. There is no `sorry`, `admit`,
  custom `axiom`, `unsafe`, or `@[implemented_by]` (verified by
  `scripts/check_forbidden.sh` and `rg`), and every principal theorem depends only on
  `propext`, `Classical.choice`, `Quot.sound` (`#print axioms`).
* **Does NOT guarantee by itself:** that a theorem *statement* faithfully captures the
  intended mathematical claim. A vacuous or mis-quantified statement can be
  kernel-checked and still be worthless. Semantic fidelity is a separate obligation.

## Semantic audits performed

* `docs/proofs/PRINCIPAL_THEOREMS.md`: exact Lean statements, English readings, edge cases, and a
  fidelity verdict for each of the seven public results.
* `docs/proofs/INDEPENDENT_PROOF_AUDIT.md`: an informal proof of each principal theorem
  reconstructed *from the Lean definitions*, checking every specific correctness point
  (event count, disjointness, orientation of the triangular argument, ambient exterior
  dimension, rectangular moment-curve case, ground-set-larger-than-`a+b`, etc.).
* `docs/proofs/SEMANTIC_AUDIT.md`: quantifier order, finiteness of index types, direction of
  cross-intersection (`i≠j` vs. `i<j`), `Disjoint` = empty intersection, nonzero
  denominators, actual `⊓` in the subspace theorem, non-vacuity witnesses.
* `docs/proofs/ADVERSARIAL_TESTS.md`: each principal hypothesis shown load-bearing by an explicit
  counterexample to the weakened claim.

## What was independently checked computationally

* `scripts/verify_small_cases.py`: exhaustive exact-rational checks of the weighted,
  uniform, and skew bounds and the sharpness construction (`OVERALL: PASS`).
* `scripts/adversarial_checks.py`: exact counterexamples witnessing that dropping a
  hypothesis breaks each theorem (`OVERALL: PASS`).
* `RequestProject/Examples.lean`: `decide`/`norm_num` regression checks of binomial
  values, the closed-form separation count over five boundary cases, and adversarial
  sums exceeding 1.

These computational checks are regression tests corroborating the theorems on small
instances; they are **not** substitutes for the machine-checked proofs.

## What still requires human understanding

* Confirming that the formal statements match the intended informal theorems (the
  audits argue this; a human should read and agree).
* Judging historical attribution and novelty claims (`docs/research/NOVELTY_AUDIT.md`,
  `docs/research/BIBLIOGRAPHY_AUDIT.md`), especially the external-library search, which could not be
  run against live indexes here.
* Reviewing the intricate finite-bijection proof in `SeparationEvents.lean`.

`docs/review/HUMAN_REVIEW_GUIDE.md` and `docs/review/ORAL_DEFENSE_QUESTIONS.md` are provided specifically to
help a human author reach genuine understanding.

## Responsibility

Kernel-checking is not a substitute for human judgment about statements, attribution,
and significance. The human author, Louis Gestin, remains fully responsible for every claim in the paper
and documentation. AI assistance is disclosed here and in the paper; **no AI
system is listed as an author**, and the presence of AI assistance is not treated as
irrelevant merely because Lean checked the code.


## Documentation index

The detailed audit files are grouped under [`docs/`](docs/README.md).
