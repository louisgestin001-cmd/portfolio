# Louis Gestin — Portfolio

French student interested in **artificial intelligence, formal mathematics, programming, and software development**.

- **Location:** France
- **Contact:** [louis@gestin.net](mailto:louis@gestin.net)
- **Current tools:** Python, Lean 4, LaTeX, Git, GitHub Actions, and AI-assisted development

This repository is the central home for my technical projects. Each project includes its own documentation, reproducibility instructions, limitations, and—when relevant—a precise statement describing how artificial intelligence was used.

[![Two-Families Lean checks](https://github.com/louisgestin001-cmd/portfolio/actions/workflows/two-families-ci.yml/badge.svg)](https://github.com/louisgestin001-cmd/portfolio/actions/workflows/two-families-ci.yml)

## Projects

### Two-Families Theorems in Lean 4

A reproducible Lean 4 / Mathlib development covering classical two-families results in extremal combinatorics and linear algebra.

**Highlights**

- 13 Lean source files and 37 theorem declarations;
- two proof routes: permutation counting and exterior algebra;
- exact Python regression tests and adversarial counterexamples;
- English and French technical reports;
- semantic, dependency, bibliography, and proof audits;
- automated verification with GitHub Actions;
- detailed disclosure of substantial AI assistance throughout the workflow.

**Open the project:** [`projects/two-families-lean/`](projects/two-families-lean/README.md)

**Reports:** [English PDF](projects/two-families-lean/paper/main.pdf) · [French PDF](projects/two-families-lean/paper/main_fr.pdf)

**AI disclosure:** [`AI_USE_STATEMENT.md`](projects/two-families-lean/AI_USE_STATEMENT.md)

> This project formalizes known mathematics. It does not claim a new theorem or unaided authorship.

## Compétences présentées

- structuration et documentation d'un projet technique complexe ;
- programmation en Python et formalisation vérifiée avec Lean 4 ;
- tests reproductibles et intégration continue ;
- rédaction technique bilingue français–anglais ;
- utilisation transparente et critique des outils d'intelligence artificielle.

## Repository structure

```text
portfolio/
├── README.md
├── LICENSE
├── .github/workflows/
│   └── two-families-ci.yml
└── projects/
    └── two-families-lean/
        ├── RequestProject/
        ├── paper/
        ├── scripts/
        ├── docs/
        └── README.md
```

Future projects will be added under `projects/`, while this README remains the main index.

## AI transparency

Artificial intelligence is treated as a development tool, not hidden authorship. The scope of AI assistance is documented inside each relevant project. For the current Lean project, AI contributed substantially to planning, research support, proof development, code, tests, documentation, translation, auditing, and presentation. I directed the work, selected the verification strategy and final material, and remain responsible for understanding and presenting the published claims.

## License

The source code in this portfolio is available under the [MIT License](LICENSE). Individual projects may contain their own license and attribution information. Personal texts, identity elements, logos, screenshots, and visual assets are not automatically granted for reuse unless their project states otherwise.
