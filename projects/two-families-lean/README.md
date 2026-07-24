# Two-Families Theorems in Lean 4

A reproducible Lean 4 / Mathlib formalization of classical **two-families theorems** in extremal combinatorics and linear algebra. It combines two proof technologies with a bridge between them:

1. permutation counting for Bollobás's weighted set-pairs inequality;
2. exterior algebra for the Lovász–Frankl subspace theorem;
3. a moment-curve construction connecting the subspace result to the Frankl–Kalai skew set theorem.

**This repository formalizes known mathematics. It does not claim a new theorem.**


## Author

**Louis Gestin** — French student interested in artificial intelligence, formal mathematics, and software development.

- **Location:** France
- **Contact:** [louis@gestin.net](mailto:louis@gestin.net)
- **Technologies:** Lean 4, Python, LaTeX, Git, and GitHub Actions
- **Project role:** initiated and scoped the project, directed the AI-assisted workflow, selected the verification strategy, reviewed the outputs, organized the repository, and takes responsibility for understanding and presenting the published work.

Only the professional contact address above is included in this public repository.

## Résumé en français

Ce projet formalise en Lean 4 plusieurs théorèmes classiques sur des familles de paires d'ensembles et de sous-espaces. Il contient les preuves vérifiées par le noyau de Lean, des tests Python sur de petits cas, des contre-exemples lorsque certaines hypothèses sont retirées, ainsi qu'un rapport technique en français et en anglais.

Le projet a été réalisé avec une assistance importante d'IA pendant l'ensemble du processus : cadrage, recherche, développement des preuves, code, tests, documentation, traduction, audits et préparation du dépôt. Cette utilisation est déclarée précisément dans [`AI_USE_STATEMENT.md`](AI_USE_STATEMENT.md). Le but est de présenter un travail vérifiable et compris, sans faire croire que chaque ligne a été produite sans assistance.

## The idea in one minute

Suppose we have pairs of finite sets $(A_i,B_i)$ such that:

- each pair is disjoint: $A_i \cap B_i = \varnothing$;
- different pairs cross-intersect: $A_i \cap B_j \neq \varnothing$ whenever $i \neq j$.

Bollobás's inequality bounds how many such pairs can coexist. In the uniform case, if every $A_i$ has size $a$ and every $B_i$ has size $b$, then

$$
m \leq \binom{a+b}{a}.
$$

A smallest sharp example uses $a=b=1$:

- $(A_1,B_1)=(\{1\},\{2\})$;
- $(A_2,B_2)=(\{2\},\{1\})$.

There are exactly two pairs, matching $\binom{2}{1}=2$.

## What the repository demonstrates

- a multi-file Lean 4 development with **13 source files** and **37 theorem declarations**;
- two substantially different formal proof routes;
- exact small-case regression tests in Python;
- adversarial counterexamples showing why key hypotheses matter;
- semantic audits separating “Lean accepts the proof” from “the statement means what we intended”;
- bilingual technical communication in English and French;
- automated GitHub Actions verification.

Current source statistics can be reproduced with:

```bash
python3 scripts/statistics.py
```

## Human contribution and AI assistance

This is an AI-assisted project, not a claim of unaided authorship. AI tools were used across the complete workflow rather than only for the Lean formalization.

The human project role includes:

- choosing the topic, objectives, constraints, and publication format;
- directing iterations and deciding which approaches, checks, and revisions to pursue;
- requesting independent checks, adversarial tests, clearer explanations, and repository improvements;
- reviewing, selecting, organizing, and publishing the resulting material;
- taking responsibility for understanding any claim presented in a portfolio or oral discussion.

Aristotle by Harmonic and other AI assistance contributed substantially to planning, research support, proof development, code, testing, technical writing, translation, auditing, and repository presentation. The exact scope and limits are documented in [`AI_USE_STATEMENT.md`](AI_USE_STATEMENT.md). A useful standard for evaluating this project is not “Was AI used?”, but “Can the author explain the definitions, proof strategy, verification process, and limitations?”

## What I learned

- how a multi-file Lean 4 project is structured and checked;
- the difference between computational testing and kernel-checked proof;
- why theorem hypotheses must be tested with explicit counterexamples;
- how to document extensive AI assistance honestly and precisely;
- how to make a technical repository reproducible with scripts and continuous integration.

## Start here

1. Read [`THEOREM_MAP.md`](THEOREM_MAP.md) for informal and Lean statements side by side.
2. Open [`RequestProject/Main.lean`](RequestProject/Main.lean) for the principal theorem signatures.
3. Read the [English report](paper/main.pdf) or the [French report](paper/main_fr.pdf).
4. Follow [`docs/review/HUMAN_REVIEW_GUIDE.md`](docs/review/HUMAN_REVIEW_GUIDE.md) to study the project in a sensible order.
5. Run the build and regression checks below.

## Reproduce the verification

### Requirements

- Lean toolchain from `lean-toolchain` (`leanprover/lean4:v4.28.0`);
- Mathlib revision pinned by `lakefile.toml` and `lake-manifest.json` (`v4.28.0`);
- Python 3 for the independent regression scripts.

### Lean build

```bash
lake exe cache get
lake build
```

For a clean rebuild:

```bash
lake clean
lake exe cache get
lake build
```

### Independent checks

```bash
bash scripts/check_forbidden.sh
python3 scripts/verify_small_cases.py
python3 scripts/adversarial_checks.py
python3 scripts/statistics.py
```

The two Python verification programs should finish with `OVERALL: PASS`.

## Repository layout

```text
RequestProject/          Lean definitions and proofs
  SetPairs/              permutation-counting route
  LinearAlgebra/         exterior-algebra and moment-curve route
  Main.lean              principal theorem signatures
  Examples.lean          computational Lean sanity checks

paper/                   English and French reports, LaTeX sources, bibliography
scripts/                 regression checks, audits, statistics, release helper
docs/                    detailed proofs, research context, review, upstream plans
../../.github/workflows/two-families-ci.yml  automated Lean build and regression checks
```

A complete documentation index is available in [`docs/README.md`](docs/README.md).

## Main dependency routes

```text
Permutation counting                Vandermonde / moment-curve general position
        |                                          |
Weighted Bollobás                    Lovász–Frankl subspace theorem
        |                                          |
Uniform Bollobás                     Frankl–Kalai skew set theorem
                                                   |
                                          Uniform Bollobás
```

## Reports

- **English:** [`paper/main.pdf`](paper/main.pdf), source [`paper/main.tex`](paper/main.tex)
- **Français :** [`paper/main_fr.pdf`](paper/main_fr.pdf), source [`paper/main_fr.tex`](paper/main_fr.tex)

These are independent technical reports, not peer-reviewed journal publications.

## Important limitations

- Lean kernel checking verifies a proof relative to its formal statement; it does not automatically verify historical attribution, novelty, or that the formal statement captures the intended informal theorem.
- The mathematics formalized here is classical and is not presented as a discovery.
- Computational tests cover finite small instances and serve as regression checks, not substitutes for formal proofs.
- Any portfolio presentation should be accompanied by genuine understanding of at least the core definitions, one proof route, and the role of every major hypothesis.

## License

The repository is released under the [MIT License](LICENSE).

## Aristotle attribution

This project was edited with [Aristotle](https://aristotle.harmonic.fun). When Aristotle's contribution is retained in commits, Harmonic requests attribution such as:

```text
Co-authored-by: Aristotle (Harmonic) <aristotle-harmonic@harmonic.fun>
```
