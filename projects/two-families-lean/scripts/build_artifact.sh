#!/usr/bin/env bash
# Build the reproducible bilingual artifact archive.
# Includes sources, documentation, scripts, configuration, and both compiled reports.
# Excludes build outputs (.lake), git metadata, the archive itself, and the internal
# Aristotle handoff note.
set -euo pipefail
cd "$(dirname "$0")/.."

python3 - <<'PY'
from pathlib import Path
import os
import subprocess
import zipfile

out = Path("two_families_lean_artifact.zip")

try:
    files = subprocess.check_output(["git", "ls-files"], text=True, stderr=subprocess.DEVNULL).splitlines()
except (subprocess.CalledProcessError, FileNotFoundError):
    excluded_dirs = {".git", ".lake", "__pycache__"}
    files = []
    for p in Path(".").rglob("*"):
        if not p.is_file():
            continue
        if any(part in excluded_dirs for part in p.parts):
            continue
        rel = p.as_posix().removeprefix("./")
        if rel == out.name or rel == "ARISTOTLE_SUMMARY.md":
            continue
        if p.suffix in {".olean", ".ilean", ".trace", ".ir", ".o", ".so", ".aux", ".bbl", ".blg", ".log", ".out", ".toc"}:
            continue
        files.append(rel)

files = [f for f in files if f not in {"ARISTOTLE_SUMMARY.md", out.name}]
for pdf in ("paper/main.pdf", "paper/main_fr.pdf"):
    if os.path.exists(pdf):
        files.append(pdf)

if out.exists():
    out.unlink()
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for f in sorted(set(files)):
        if os.path.isfile(f):
            z.write(f)
print(f"Wrote {out} with {len(set(files))} files")
PY
