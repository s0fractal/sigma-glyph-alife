#!/usr/bin/env python3
"""The frame for ALIFE-EXP-011 — feeding the starving under the default schedule.

Founders are ALIFE-EXP-001's, for the eighth time, read through that
experiment's own module so the fingerprint cannot drift.

What this file fixes that the preregistration leaves open is listed in
`DECISIONS.md` D92-D97 and was committed before any measurement ran. The one
number the preregistration explicitly delegates — the budget at which agents
starve mid-run — is chosen by `measure.py --dry-run` under the rule stated
here, from starvation counts alone, and recorded in the RESULT's provenance.
"""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "impl"))

import sigma_alife as al  # noqa: E402


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


EXP1 = _load("alife_exp_001_corpus", HERE.parent / "alife-exp-001" / "corpus.py")
sg = al.sg

INHERITED_FINGERPRINT = "53cc6da80f66d220"

# --- pinned by the preregistration -----------------------------------------
SEEDS = (20260825, 20260826, 20260827)
ARMS = ("a", "b", "c")
ARM_LABELS = {
    "a": "default schedule, natural sharing",
    "b": "default schedule, forced grants",
    "c": "forced grants, cull-free window",
}

# --- inherited from ALIFE-EXP-001, unchanged -------------------------------
SLICE_ATP = EXP1.SLICE_ATP          # 32
TICKS = EXP1.TICKS                  # 24

# --- the budget: chosen from a dry run, by the rule below (D92) -------------
# The preregistration says "budgets chosen so that a preregistered fraction of
# agents starve mid-run", delegates the exact number to the harness author, and
# allows the dry run to observe STARVATION COUNTS ONLY. The sweep and the
# selection rule are therefore fixed here, before the dry run, and the rule
# reads nothing but a starvation count:
#
#     take the budget in BUDGET_SWEEP whose "ever starved" fraction is closest
#     to TARGET_STARVED_FRACTION; break ties toward the smaller budget.
#
# A fraction near a half is what the experiment needs: a scenario where feeding
# is the difference for a large part of the colony and the run is not degenerate
# at either end.
BUDGET_SWEEP = (8, 12, 16, 24, 32, 48, 64, 96, 128, 256)
TARGET_STARVED_FRACTION = 0.50

# --- the commons, which ALIFE-EXP-001 did not need (D93) -------------------
# EXP-001 endows every agent and leaves the pool at zero, so `phase_share`
# cannot grant anything there. Feeding needs a commons to feed FROM. The reserve
# is deliberately far above any plausible draw; if it ever bound, C2 fails
# closed, because a truncated grant is exactly an insufficient one.
COMMONS_RESERVE = 200_000

# --- arm (a)'s rebate rate (D94) -------------------------------------------
# `phase_share` grants `int(rebate_rate * overlap)`. At 1.0 an agent is granted
# one ATP per shared node occurrence it holds, which is generously above the
# price of a next action — arm (a) is meant to show what the ENGINE's own
# feeding path does, so it must not fail for want of being switched on.
REBATE_RATE = 1.0

# --- thresholds the preregistration states in prose ------------------------
H1_EXPECTED = 0.0          # survival rate, preregistered expectation
H2_LEAK_THRESHOLD = 0.10   # fed-then-buried ATP as a share of ATP granted to starving
H3_EXPECTED = 1.0          # survival rate with a cull-free window

# The seed whose tick-level event log goes into the receipt as a worked example.
WORKED_EXAMPLE_SEED = SEEDS[0]

# Budget for the uninterrupted reference evaluation used to check that a resumed
# agent lands on the whole-run answer (H3's `resumption_bound` clause).
ORACLE_BUDGET = 400_000


def build():
    entries = EXP1.build()
    got = EXP1.fingerprint(entries)
    if got != INHERITED_FINGERPRINT:
        raise SystemExit(f"ALIFE-EXP-011 inherits the EXP-001 corpus, which has "
                         f"moved: expected {INHERITED_FINGERPRINT}, got {got}.")
    return entries


def fingerprint(entries=None):
    return EXP1.fingerprint(entries or build())


if __name__ == "__main__":
    c = build()
    print(f"founders: {len(c)} terms from ALIFE-EXP-001 at {fingerprint(c)}")
    print(f"arms: " + "; ".join(f"({k}) {v}" for k, v in ARM_LABELS.items()))
    print(f"seeds {SEEDS}, {TICKS} ticks, slice {SLICE_ATP}")
    print(f"budget chosen from {BUDGET_SWEEP} at the sweep point whose "
          f"ever-starved fraction is closest to {TARGET_STARVED_FRACTION}")
    print(f"commons reserve {COMMONS_RESERVE}, arm (a) rebate rate {REBATE_RATE}")
