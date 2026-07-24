#!/usr/bin/env python3
"""Compute simple statistics about the Lean development.

Counts non-blank/non-comment lines, `theorem`/`lemma`/`def` declarations, and
`import` lines across `RequestProject/`.
"""
from __future__ import annotations
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "RequestProject")

decl_re = re.compile(r"^\s*(?:noncomputable\s+|private\s+|protected\s+)*(theorem|lemma|def|abbrev|instance|structure)\b")
import_re = re.compile(r"^\s*import\b")
# Match a genuine `sorry` / `admit` token, but NOT `sorryAx` (which appears in the
# axiom-audit docstring of `Main.lean`). Word boundary excludes `sorryAx`.
sorry_re = re.compile(r"\b(?:sorry|admit)\b")


def main() -> int:
    total_lines = 0
    code_lines = 0
    counts = {"theorem": 0, "lemma": 0, "def": 0, "abbrev": 0, "instance": 0, "structure": 0}
    imports = 0
    sorries = 0
    files = 0
    in_block = False
    for dirpath, _, filenames in os.walk(SRC):
        for fn in sorted(filenames):
            if not fn.endswith(".lean"):
                continue
            files += 1
            with open(os.path.join(dirpath, fn), encoding="utf-8") as f:
                for line in f:
                    total_lines += 1
                    s = line.strip()
                    if not s:
                        continue
                    if sorry_re.search(s):
                        sorries += 1
                    if not s.startswith("--") and not s.startswith("/-"):
                        code_lines += 1
                    m = decl_re.match(line)
                    if m:
                        counts[m.group(1)] = counts.get(m.group(1), 0) + 1
                    if import_re.match(line):
                        imports += 1
    print(f"files:            {files}")
    print(f"total lines:      {total_lines}")
    print(f"non-blank lines:  {code_lines}")
    print(f"import lines:     {imports}")
    for k in ("theorem", "lemma", "def", "abbrev", "instance", "structure"):
        print(f"{k+':':17s} {counts.get(k,0)}")
    print(f"declarations:     {sum(counts.values())}")
    print(f"lines with sorry: {sorries}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
