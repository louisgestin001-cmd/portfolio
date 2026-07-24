#!/usr/bin/env bash
# Reject incomplete or unsafe proof shortcuts in the Lean source tree.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/RequestProject"
status=0

check_pattern() {
  local label="$1"
  local pattern="$2"
  echo "== $label =="
  if grep -RInE "$pattern" "$SRC" 2>/dev/null; then
    status=1
  else
    echo "  (none)"
  fi
}

check_pattern "sorry token" '(^|[^[:alnum:]_])sorry([^[:alnum:]_]|$)'
check_pattern "admit token" '(^|[^[:alnum:]_])admit([^[:alnum:]_]|$)'
check_pattern "custom axiom declaration" '^[[:space:]]*axiom[[:space:]]'
check_pattern "implemented_by escape hatch" '@\[implemented_by'
check_pattern "unsafe declaration" '^[[:space:]]*unsafe[[:space:]]'

echo "== native_decide outside Examples.lean =="
native_matches="$(grep -RInE '(^|[^[:alnum:]_])native_decide([^[:alnum:]_]|$)' "$SRC" --include='*.lean' 2>/dev/null || true)"
if [[ -n "$native_matches" ]]; then
  unexpected="$(printf '%s\n' "$native_matches" | grep -v '/Examples\.lean:' || true)"
  if [[ -n "$unexpected" ]]; then
    printf '%s\n' "$unexpected"
    status=1
  else
    echo "  only present in Examples.lean (allowed regression checks)"
  fi
else
  echo "  (none)"
fi

echo
if [[ "$status" -eq 0 ]]; then
  echo "OK: no forbidden declarations or proof shortcuts found."
else
  echo "ERROR: forbidden matches were found above."
fi
exit "$status"
