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

say "Chance models destroy exactly what they claim, and are sampled"
# Two experiments in a row produced a positive result that a null destroyed, and
# in both the null was drawn ONCE. The models live in impl/sigma_nulls.py now,
# with the invariants each one asserts about itself checked here.
python3 tests/alife_nulls.py | tee /dev/stderr | grep -q "ALIFE-NULLS: ALL PASS"

say "Receipt guard: every null in every receipt says how many times it was drawn"
python3 tools/receipt_guard.py | tee /dev/stderr | grep -q "RECEIPT-GUARD: ALL PASS"

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

say "ALIFE-EXP-004 replay: the adversarial replication of EXP-001's headline"
python3 experiments/alife-exp-004/measure.py --record | tail -5
if command -v git >/dev/null 2>&1 && git rev-parse --git-dir >/dev/null 2>&1; then
  git diff --exit-code experiments/alife-exp-004/results.json
else
  skip "ALIFE-EXP-004 replay was not diffed against the committed receipt (no git)"
fi

say "ALIFE-EXP-005 replay: Book I's R-S address-sharing discount"
python3 experiments/alife-exp-005/measure.py --record | tail -6
if command -v git >/dev/null 2>&1 && git rev-parse --git-dir >/dev/null 2>&1; then
  git diff --exit-code experiments/alife-exp-005/results.json
else
  skip "ALIFE-EXP-005 replay was not diffed against the committed receipt (no git)"
fi

say "ALIFE-EXP-003 replay: the committed receipt must be what it derives"
python3 experiments/alife-exp-003/measure.py --record | tail -4
if command -v git >/dev/null 2>&1 && git rev-parse --git-dir >/dev/null 2>&1; then
  git diff --exit-code experiments/alife-exp-003/results.json
else
  skip "ALIFE-EXP-003 replay was not diffed against the committed receipt (no git)"
fi

say "ALIFE-EXP-008: controls only (the replay is a ten-minute job)"
# C1 is three hand cases rather than one: the self-maintenance condition is the
# only thing that separates this from EXP-007's history-core, and a peeling bug
# in it would produce organizations from anything.
python3 experiments/alife-exp-008/measure.py --controls \
  | tee /dev/stderr | grep -q "EXP-008-CONTROLS: ALL PASS"
if [[ "${EXP007_ELSEWHERE:-0}" != "1" && "${RUN_SLOW:-0}" != "1" ]]; then
  skip "ALIFE-EXP-008 full replay (ten minutes) — set RUN_SLOW=1, or let its own workflow run it"
elif [[ "${RUN_SLOW:-0}" = "1" ]]; then
  python3 experiments/alife-exp-008/measure.py --record | tail -6
  if command -v git >/dev/null 2>&1 && git rev-parse --git-dir >/dev/null 2>&1; then
    git diff --exit-code experiments/alife-exp-008/results.json
  fi
else
  printf '\n(ALIFE-EXP-008 full replay runs in its own workflow on this commit)\n'
fi

say "ALIFE-EXP-007: controls only (the replay is a ten-minute job)"
# Every control runs here, including C5 — the one that proves the core algorithm
# returns nothing on an open chain, without which a peeling bug produces cores
# from anything. The full replay lives in .github/workflows/exp-007.yml, path
# filtered, on the sigma-glyph exp-004 precedent.
if [[ "${RUN_SLOW:-0}" = "1" ]]; then
  python3 experiments/alife-exp-007/measure.py --record | tail -6
  if command -v git >/dev/null 2>&1 && git rev-parse --git-dir >/dev/null 2>&1; then
    git diff --exit-code experiments/alife-exp-007/results.json
  fi
else
  python3 experiments/alife-exp-007/measure.py --controls \
    | tee /dev/stderr | grep -q "EXP-007-CONTROLS: ALL PASS"
  if [[ "${EXP007_ELSEWHERE:-0}" = "1" ]]; then
    # Not a skip: the surface IS checked, by .github/workflows/exp-007.yml on the
    # same commit. Blanket ALLOW_SKIPS would have accepted every other gap too —
    # a missing `lean`, an unreachable validator — so the exemption is named and
    # scoped to the one surface another job covers.
    printf '\n(ALIFE-EXP-007 full replay runs in its own workflow on this commit)\n'
  else
    skip "ALIFE-EXP-007 full replay (ten minutes) — set RUN_SLOW=1, or let its own workflow run it"
  fi
fi

say "ALIFE-EXP-006 replay: what resumption is worth, in agents"
python3 experiments/alife-exp-006/measure.py --record | tail -4
if command -v git >/dev/null 2>&1 && git rev-parse --git-dir >/dev/null 2>&1; then
  git diff --exit-code experiments/alife-exp-006/results.json
else
  skip "ALIFE-EXP-006 replay was not diffed against the committed receipt (no git)"
fi

say "ALIFE-EXP-005 addendum: where the copy-pricing discount binds"
# Post hoc and by a different author from the harness, so it is run separately
# and its receipt is diffed separately.
python3 experiments/alife-exp-005/addendum_scarcity.py --record | tail -3
if command -v git >/dev/null 2>&1 && git rev-parse --git-dir >/dev/null 2>&1; then
  git diff --exit-code experiments/alife-exp-005/addendum_scarcity.json
else
  skip "EXP-005 addendum was not diffed against its committed receipt (no git)"
fi

say "Analysis: the ceiling's slack decomposition re-derives from committed receipts"
# Descriptive, not an experiment — it takes no measurement. It is gated anyway,
# because it states numbers about this repository's own published results and
# nothing else would notice if a receipt moved underneath it.
python3 experiments/analysis-001-where-the-slack-lives/analyse.py --record | tail -3
if command -v git >/dev/null 2>&1 && git rev-parse --git-dir >/dev/null 2>&1; then
  git diff --exit-code experiments/analysis-001-where-the-slack-lives/analysis.json
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
