#!/usr/bin/env bash
# The complete validation matrix, one command. Run from the repository root:
#   tools/test-all.sh
# Env: SIGMA_GLYPH        — the impl/ directory of a sigma-glyph checkout
#      SIGMA_GLYPH_PROOFS — its proofs/ directory (for the premise guard)
# Both are found automatically when sigma-glyph sits beside this repository.
set -euo pipefail
cd "$(dirname "$0")/.."

say() { printf '\n=== %s ===\n' "$1"; }

# A skipped surface is not a passed one. sigma-glyph's tools/test-all.sh printed
# ALL GREEN after silently skipping its Lean bridges; this counts and names every
# skip, and says so in the exit status. ALLOW_SKIPS=1 is how an operator states
# the gap was accepted on purpose.
SKIPPED=""
skip() { SKIPPED="$SKIPPED  - $1"$'\n'; printf '\n(skipping: %s)\n' "$1"; }

say "Substrate self-test (Book I oracle resolved, driver, economy, metrics)"
python3 impl/sigma_alife.py | tee /dev/stderr | grep -q "ALIFE: ALL PASS"

say "Differential: the driver IS the oracle, whole / sliced / starved-and-refed"
# The one place this repository is allowed to differ from Book I is the outcome
# on exhaustion (ALIFE-ADR-001 §5). This is the fence that keeps it there, and
# it fails closed if no case ever starved.
python3 tests/alife_differential.py --terms 80 \
  | tee /dev/stderr | grep -q "ALIFE-DIFFERENTIAL: ALL AGREE"

say "Population properties + the negative controls that prove they can fail"
python3 tests/alife_conservation.py | tee /dev/stderr | grep -q "ALIFE-CONSERVATION: ALL PASS"

say "Memoization: the answer does not move, and the price is not a free choice"
# The memo is the one place this repository prices an action Book I does not
# have. M3 is a control that must FAIL: at a flat price the memory bound breaks.
python3 tests/alife_memo.py | tee /dev/stderr | grep -q "ALIFE-MEMO: ALL PASS"

say "Guard regression: every gate puts its verdict in the EXIT STATUS"
python3 tests/exit_status_guard.py | tee /dev/stderr | grep -q "EXIT-STATUS-GUARD: ALL PASS"

say "Proofs: pinned statements, no sorries, premise identical to sigma-glyph"
set +e
python3 proofs/premise_guard.py | tee /dev/stderr | grep -q "PREMISE-GUARD: ALL PASS"
guard=$?
set -e
if [[ $guard -ne 0 ]]; then
  # The guard exits 2 when it could only check the text (no `lean`, or no
  # sigma-glyph checkout to compare the copied premise against) and 1 when
  # something actually failed. Only the first is a skip.
  python3 proofs/premise_guard.py >/dev/null 2>&1 || rc=$?
  if [[ "${rc:-0}" -eq 2 ]]; then
    skip "proofs: lean and/or the sigma-glyph proofs were not reachable"
  else
    echo "PREMISE-GUARD FAILED"; exit 1
  fi
fi

say "ALIFE-EXP-001 replay: the committed receipt must be what it derives"
# Re-derive rather than check-only: check-only does not write the file, so a
# diff after it would compare nothing at all. `--record` writes only after every
# control has passed, so a failure stops before the file is touched.
python3 experiments/alife-exp-001/measure.py --record | tail -6
if command -v git >/dev/null 2>&1 && git rev-parse --git-dir >/dev/null 2>&1; then
  git diff --exit-code experiments/alife-exp-001/results.json
else
  skip "experiment replay was not diffed against the committed receipt (no git)"
fi

say "The need packet reproduces what it claims"
# sigma-glyph's own lesson: papers stated numbers about the repository and
# nothing enforced them. A need packet is a document that states numbers about
# somebody else's repository, which is worse. It runs here on every push.
python3 needs/DA-SIGMA-0002-memo-pricing/fixtures/reproduce.py \
  | tee /dev/stderr | grep -q "DA-SIGMA-0002: REPRODUCED"
if [[ -n "${DECISION_ARCHAEOLOGY:-}" && -f "$DECISION_ARCHAEOLOGY/tools/validate_need.py" ]]; then
  python3 "$DECISION_ARCHAEOLOGY/tools/validate_need.py" needs/DA-SIGMA-0002-memo-pricing \
    | tee /dev/stderr | grep -q "^PASS"
else
  skip "need packet not validated against decision-archaeology.need@v0 — set DECISION_ARCHAEOLOGY to a checkout"
fi

say "ALIFE-EXP-002 replay: the committed receipt must be what it derives"
python3 experiments/alife-exp-002/measure.py --record | tail -4
if command -v git >/dev/null 2>&1 && git rev-parse --git-dir >/dev/null 2>&1; then
  git diff --exit-code experiments/alife-exp-002/results.json
else
  skip "ALIFE-EXP-002 replay was not diffed against the committed receipt (no git)"
fi

if [[ -n "$SKIPPED" ]]; then
  printf '\nTEST-ALL: NOT COMPLETE — these surfaces were not checked:\n%s' "$SKIPPED"
  if [[ "${ALLOW_SKIPS:-0}" = "1" ]]; then
    printf 'ALLOW_SKIPS=1: the gap above was accepted deliberately.\n'; exit 0
  fi
  printf 'A skipped surface is not a passed one. Set ALLOW_SKIPS=1 to accept it.\n'
  exit 2
fi
printf '\nTEST-ALL: ALL GREEN\n'
